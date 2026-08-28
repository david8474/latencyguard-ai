import json
from pathlib import Path

from verifier import verify

INCIDENTS_PATH = Path(__file__).resolve().parents[1] / "data" / "incidents.json"


def load_incident(incident_id):
    with INCIDENTS_PATH.open(encoding="utf-8") as file:
        incidents = json.load(file)
    return next(incident for incident in incidents if incident["id"] == incident_id)


def test_case_14_cpu_saturation_is_unverified_when_latency_is_healthy():
    incident = load_incident(14)
    result = verify(incident, "cpu_saturation")

    assert result["verified"] is False
    assert result["confidence"] == "low"
    evidence_by_metric = {item["metric"]: item for item in result["evidence"]}
    assert evidence_by_metric["cpu_percent"]["passed"] is True
    assert evidence_by_metric["elevated_latency"]["passed"] is False


def test_case_13_traffic_spike_is_unverified_when_latency_is_healthy():
    incident = load_incident(13)
    result = verify(incident, "traffic_spike")

    assert result["verified"] is False
    assert result["confidence"] == "low"
    evidence_by_metric = {item["metric"]: item for item in result["evidence"]}
    assert evidence_by_metric["request_ratio"]["passed"] is True
    assert evidence_by_metric["elevated_latency"]["passed"] is False


def test_case_10_traffic_spike_is_verified_with_database_latency_competitor():
    incident = load_incident(10)
    result = verify(incident, "traffic_spike")

    assert result["verified"] is True
    assert result["confidence"] == "medium"
    assert "database_latency" in result["competing_patterns"]


def test_clearly_supported_database_latency_is_verified_with_high_confidence():
    incident = load_incident(1)
    result = verify(incident, "database_latency")

    assert result["verified"] is True
    assert result["confidence"] == "high"
    assert result["competing_patterns"] == []


def test_unknown_diagnosis_is_unverified_with_low_confidence():
    incident = load_incident(1)
    result = verify(incident, "mystery_cause")

    assert result["verified"] is False
    assert result["confidence"] == "low"
    assert result["diagnosis"] == "mystery_cause"
