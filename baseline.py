def diagnose_baseline(incident):
    if incident["cpu_percent"] >= 90:
        return "cpu_saturation"

    if incident["db_latency_ms"] >= 800:
        return "database_latency"

    if incident["error_rate"] >= 0.10:
        return "application_errors"

    if incident["memory_percent"] >= 90:
        return "memory_pressure"

    if incident["request_rate"] >= 1000:
        return "traffic_spike"

    if (
        incident["p99_ms"] >= 1500
        and incident["p95_ms"] < 500
    ):
        return "tail_latency_anomaly"

    return "normal"