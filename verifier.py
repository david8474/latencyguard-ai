CPU_SATURATION_PERCENT = 90
MEMORY_PRESSURE_PERCENT = 90
ERROR_RATE_THRESHOLD = 0.10
DB_LATENCY_MS = 700
TRAFFIC_SPIKE_RATIO = 2.0
P95_ELEVATED_MS = 500
P99_ELEVATED_MS = 1500
TAIL_P99_MS = 1500
TAIL_P95_MAX_MS = 500

ABNORMAL_PATTERNS = (
    "application_errors",
    "traffic_spike",
    "cpu_saturation",
    "memory_pressure",
    "database_latency",
    "tail_latency_anomaly",
)


def _request_ratio(incident):
    baseline_rate = incident["baseline_request_rate"]
    if baseline_rate <= 0:
        return 0.0
    return incident["request_rate"] / baseline_rate


def _elevated_latency(incident):
    return (
        incident["p95_ms"] >= P95_ELEVATED_MS
        or incident["p99_ms"] >= P99_ELEVATED_MS
    )


def _check(metric, value, comparison, threshold, passed):
    return {
        "metric": metric,
        "value": value,
        "comparison": comparison,
        "threshold": threshold,
        "passed": passed,
    }


def _elevated_latency_check(incident):
    p95 = incident["p95_ms"]
    p99 = incident["p99_ms"]
    passed = _elevated_latency(incident)
    return {
        "metric": "elevated_latency",
        "value": {"p95_ms": p95, "p99_ms": p99},
        "comparison": "p95_ms >= or p99_ms >=",
        "threshold": {"p95_ms": P95_ELEVATED_MS, "p99_ms": P99_ELEVATED_MS},
        "passed": passed,
        "detail": (
            f"p95_ms={p95} >= {P95_ELEVATED_MS} or "
            f"p99_ms={p99} >= {P99_ELEVATED_MS}"
        ),
    }


def _application_errors_complete(incident):
    error_rate = incident["error_rate"]
    passed = error_rate >= ERROR_RATE_THRESHOLD
    evidence = [
        _check("error_rate", error_rate, ">=", ERROR_RATE_THRESHOLD, passed)
    ]
    return passed, evidence


def _traffic_spike_complete(incident):
    ratio = _request_ratio(incident)
    ratio_passed = ratio >= TRAFFIC_SPIKE_RATIO
    latency_check = _elevated_latency_check(incident)
    evidence = [
        {
            "metric": "request_ratio",
            "value": ratio,
            "comparison": ">=",
            "threshold": TRAFFIC_SPIKE_RATIO,
            "passed": ratio_passed,
            "detail": (
                f"request_rate={incident['request_rate']} / "
                f"baseline_request_rate={incident['baseline_request_rate']} "
                f"= {ratio}"
            ),
        },
        latency_check,
    ]
    return ratio_passed and latency_check["passed"], evidence


def _cpu_saturation_complete(incident):
    cpu = incident["cpu_percent"]
    cpu_passed = cpu >= CPU_SATURATION_PERCENT
    latency_check = _elevated_latency_check(incident)
    evidence = [
        _check("cpu_percent", cpu, ">=", CPU_SATURATION_PERCENT, cpu_passed),
        latency_check,
    ]
    return cpu_passed and latency_check["passed"], evidence


def _memory_pressure_complete(incident):
    memory = incident["memory_percent"]
    memory_passed = memory >= MEMORY_PRESSURE_PERCENT
    latency_check = _elevated_latency_check(incident)
    evidence = [
        _check(
            "memory_percent",
            memory,
            ">=",
            MEMORY_PRESSURE_PERCENT,
            memory_passed,
        ),
        latency_check,
    ]
    return memory_passed and latency_check["passed"], evidence


def _database_latency_complete(incident):
    db_latency = incident["db_latency_ms"]
    db_passed = db_latency >= DB_LATENCY_MS
    latency_check = _elevated_latency_check(incident)
    evidence = [
        _check("db_latency_ms", db_latency, ">=", DB_LATENCY_MS, db_passed),
        latency_check,
    ]
    return db_passed and latency_check["passed"], evidence


def _tail_latency_anomaly_complete(incident):
    p99 = incident["p99_ms"]
    p95 = incident["p95_ms"]
    p99_passed = p99 >= TAIL_P99_MS
    p95_passed = p95 < TAIL_P95_MAX_MS
    evidence = [
        _check("p99_ms", p99, ">=", TAIL_P99_MS, p99_passed),
        _check("p95_ms", p95, "<", TAIL_P95_MAX_MS, p95_passed),
    ]
    return p99_passed and p95_passed, evidence


_ABNORMAL_CHECKERS = {
    "application_errors": _application_errors_complete,
    "traffic_spike": _traffic_spike_complete,
    "cpu_saturation": _cpu_saturation_complete,
    "memory_pressure": _memory_pressure_complete,
    "database_latency": _database_latency_complete,
    "tail_latency_anomaly": _tail_latency_anomaly_complete,
}


def _normal_complete(incident):
    evidence = []
    any_abnormal = False

    for name in ABNORMAL_PATTERNS:
        complete, pattern_evidence = _ABNORMAL_CHECKERS[name](incident)
        if complete:
            any_abnormal = True
        evidence.append(
            {
                "metric": f"{name}_complete",
                "value": complete,
                "comparison": "==",
                "threshold": False,
                "passed": not complete,
                "detail": pattern_evidence,
            }
        )

    return (not any_abnormal), evidence


_PATTERN_CHECKERS = {
    **_ABNORMAL_CHECKERS,
    "normal": _normal_complete,
}


def _complete_patterns(incident):
    complete = []
    for name in ABNORMAL_PATTERNS:
        is_complete, _ = _ABNORMAL_CHECKERS[name](incident)
        if is_complete:
            complete.append(name)

    is_normal, _ = _normal_complete(incident)
    if is_normal:
        complete.append("normal")

    return complete


def verify(incident: dict, diagnosis: str) -> dict:
    checker = _PATTERN_CHECKERS.get(diagnosis)

    if checker is None:
        complete = _complete_patterns(incident)
        return {
            "diagnosis": diagnosis,
            "verified": False,
            "evidence": [
                {
                    "metric": "diagnosis",
                    "value": diagnosis,
                    "comparison": "in",
                    "threshold": list(_PATTERN_CHECKERS.keys()),
                    "passed": False,
                    "detail": "no complete-pattern check defined for diagnosis",
                }
            ],
            "confidence": "low",
            "competing_patterns": complete,
        }

    pattern_complete, evidence = checker(incident)
    complete = _complete_patterns(incident)
    competing = [name for name in complete if name != diagnosis]

    if pattern_complete:
        confidence = "medium" if competing else "high"
    else:
        confidence = "low"

    return {
        "diagnosis": diagnosis,
        "verified": pattern_complete,
        "evidence": evidence,
        "confidence": confidence,
        "competing_patterns": competing,
    }
