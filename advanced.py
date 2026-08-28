CPU_SATURATION_PERCENT = 90
MEMORY_PRESSURE_PERCENT = 90
ERROR_RATE_THRESHOLD = 0.10
DB_LATENCY_MS = 700
TRAFFIC_SPIKE_RATIO = 2.0
P95_ELEVATED_MS = 500
P99_ELEVATED_MS = 1500
TAIL_P99_MS = 1500
TAIL_P95_MAX_MS = 500


def _has_elevated_latency(incident):
    return (
        incident["p95_ms"] >= P95_ELEVATED_MS
        or incident["p99_ms"] >= P99_ELEVATED_MS
    )


def _request_ratio(incident):
    baseline_rate = incident["baseline_request_rate"]
    if baseline_rate <= 0:
        return 0.0
    return incident["request_rate"] / baseline_rate


def diagnose_advanced(incident):
    if incident["error_rate"] >= ERROR_RATE_THRESHOLD:
        return "application_errors"

    if (
        _request_ratio(incident) >= TRAFFIC_SPIKE_RATIO
        and _has_elevated_latency(incident)
    ):
        return "traffic_spike"

    if (
        incident["cpu_percent"] >= CPU_SATURATION_PERCENT
        and _has_elevated_latency(incident)
    ):
        return "cpu_saturation"

    if (
        incident["memory_percent"] >= MEMORY_PRESSURE_PERCENT
        and _has_elevated_latency(incident)
    ):
        return "memory_pressure"

    if (
        incident["db_latency_ms"] >= DB_LATENCY_MS
        and _has_elevated_latency(incident)
    ):
        return "database_latency"

    if (
        incident["p99_ms"] >= TAIL_P99_MS
        and incident["p95_ms"] < TAIL_P95_MAX_MS
    ):
        return "tail_latency_anomaly"

    return "normal"
