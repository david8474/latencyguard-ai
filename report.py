from advanced import diagnose_advanced
from verifier import verify

SAFETY_NOTE = "No production changes were automatically performed."

_INVESTIGATION_STEPS = {
    "application_errors": [
        "Inspect recent error logs and exception traces.",
        "Identify failing endpoints and response status codes.",
        "Check whether a recent deploy or config change correlates.",
    ],
    "traffic_spike": [
        "Confirm request_rate versus baseline_request_rate.",
        "Identify the source of the extra traffic.",
        "Review whether latency rose with the traffic increase.",
    ],
    "cpu_saturation": [
        "Identify CPU-heavy processes, threads, or endpoints.",
        "Compare CPU saturation with current latency.",
        "Check for recent code or load-mix changes.",
    ],
    "memory_pressure": [
        "Inspect memory growth, GC, and cache size.",
        "Look for leak or allocation patterns.",
        "Compare memory pressure with current latency.",
    ],
    "database_latency": [
        "Inspect slow queries, locks, and wait events.",
        "Check database connections and replication lag.",
        "Review recent query or schema changes.",
    ],
    "tail_latency_anomaly": [
        "Inspect p99 outlier traces and timeout paths.",
        "Check GC pauses, retries, and cache misses.",
        "Compare p99 against a healthy p95.",
    ],
    "normal": [
        "Confirm no abnormal pattern is complete.",
        "Continue routine latency and error monitoring.",
        "Revisit only if latency or errors worsen.",
    ],
}


def _summary(diagnosis, verification):
    if not verification["verified"]:
        return (
            f"Diagnosis {diagnosis} is not confirmed "
            f"(confidence={verification['confidence']})."
        )

    if verification["confidence"] == "medium":
        competing = ", ".join(verification["competing_patterns"])
        return (
            f"Verified {diagnosis} with medium confidence; "
            f"also complete: {competing}."
        )

    return f"Verified {diagnosis} with high confidence."


def _competing_cause_step(diagnosis, competing):
    if len(competing) == 1:
        return (
            f"Investigate competing cause {competing[0]} "
            "before taking action."
        )
    return (
        "Investigate competing causes "
        + ", ".join(competing)
        + " before taking action."
    )


def _recommendations(diagnosis, verification):
    lines = []

    if not verification["verified"]:
        lines.append(f"Diagnosis {diagnosis} is not confirmed.")
        competing = verification["competing_patterns"]
        if competing:
            lines.append(_competing_cause_step(diagnosis, competing))
        lines.append("Review failed evidence checks before taking action.")
        return lines[:4]

    if (
        verification["confidence"] == "medium"
        and verification["competing_patterns"]
    ):
        lines.append(
            _competing_cause_step(
                diagnosis, verification["competing_patterns"]
            )
        )

    steps = _INVESTIGATION_STEPS.get(
        diagnosis,
        ["Review incident metrics and traces."],
    )
    lines.extend(steps)
    return lines[:4]


def _format_evidence_line(item):
    status = "passed" if item["passed"] else "failed"
    detail = item.get("detail")
    if isinstance(detail, str):
        return f"- {item['metric']}: {detail} ({status})"
    return (
        f"- {item['metric']}: {item['value']} "
        f"{item['comparison']} {item['threshold']} ({status})"
    )


def generate_report(incident, diagnosis=None):
    if diagnosis is None:
        diagnosis = diagnose_advanced(incident)

    verification = verify(incident, diagnosis)
    competing = list(verification["competing_patterns"])

    return {
        "incident_id": incident["id"],
        "service": incident["service"],
        "diagnosis": diagnosis,
        "verified": verification["verified"],
        "confidence": verification["confidence"],
        "competing_patterns": competing,
        "evidence": verification["evidence"],
        "summary": _summary(diagnosis, verification),
        "recommendations": _recommendations(diagnosis, verification),
        "safety_note": SAFETY_NOTE,
    }


def format_report(report):
    competing = report["competing_patterns"]
    competing_text = ", ".join(competing) if competing else "none"
    verified_text = "yes" if report["verified"] else "no"
    evidence_lines = [
        _format_evidence_line(item) for item in report["evidence"]
    ]
    recommendation_lines = [
        f"- {step}" for step in report["recommendations"]
    ]

    sections = [
        "Incident Report",
        "===============",
        f"ID: {report['incident_id']}",
        f"Service: {report['service']}",
        f"Diagnosis: {report['diagnosis']}",
        f"Verified: {verified_text}",
        f"Confidence: {report['confidence']}",
        f"Competing patterns: {competing_text}",
        "",
        "Summary",
        "-------",
        report["summary"],
        "",
        "Evidence",
        "--------",
        *evidence_lines,
        "",
        "Recommended investigation",
        "-------------------------",
        *recommendation_lines,
        "",
        report["safety_note"],
    ]
    return "\n".join(sections)
