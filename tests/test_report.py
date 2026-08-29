import json
from pathlib import Path

from advanced import diagnose_advanced
from report import SAFETY_NOTE, format_report, generate_report
from verifier import verify

INCIDENTS_PATH = Path(__file__).resolve().parents[1] / "data" / "incidents.json"


def load_incident(incident_id):
    with INCIDENTS_PATH.open(encoding="utf-8") as file:
        incidents = json.load(file)
    return next(incident for incident in incidents if incident["id"] == incident_id)


def test_safety_note_is_exact():
    assert SAFETY_NOTE == "No production changes were automatically performed."


def test_case_1_high_confidence_database_latency_report():
    incident = load_incident(1)
    report = generate_report(incident)

    assert report["incident_id"] == 1
    assert report["service"] == "checkout-api"
    assert report["diagnosis"] == "database_latency"
    assert report["verified"] is True
    assert report["confidence"] == "high"
    assert report["competing_patterns"] == []
    assert report["safety_note"] == SAFETY_NOTE
    assert len(report["recommendations"]) <= 4
    assert len(report["recommendations"]) >= 2
    assert "not confirmed" not in report["summary"]
    assert all(
        "competing cause" not in step for step in report["recommendations"]
    )
    assert any("slow queries" in step for step in report["recommendations"])


def test_case_10_medium_confidence_surfaces_competitor_first():
    incident = load_incident(10)
    report = generate_report(incident)

    assert report["diagnosis"] == "traffic_spike"
    assert report["verified"] is True
    assert report["confidence"] == "medium"
    assert "database_latency" in report["competing_patterns"]
    assert len(report["recommendations"]) <= 4

    first = report["recommendations"][0]
    assert "database_latency" in first
    assert first.startswith("Investigate competing cause")
    assert "before taking action" in first

    later = report["recommendations"][1:]
    assert any("request_rate" in step for step in later)
    assert all("database_latency" not in step for step in later)


def test_unverified_diagnosis_says_not_confirmed():
    incident = load_incident(14)
    report = generate_report(incident, diagnosis="cpu_saturation")

    assert report["verified"] is False
    assert report["confidence"] == "low"
    assert "not confirmed" in report["summary"]
    assert report["recommendations"][0] == (
        "Diagnosis cpu_saturation is not confirmed."
    )
    assert len(report["recommendations"]) <= 4
    assert all(
        "restart" not in step.lower() for step in report["recommendations"]
    )


def test_unknown_diagnosis_is_not_confirmed():
    incident = load_incident(1)
    report = generate_report(incident, diagnosis="mystery_cause")

    assert report["verified"] is False
    assert report["confidence"] == "low"
    assert "not confirmed" in report["summary"]
    assert report["recommendations"][0] == (
        "Diagnosis mystery_cause is not confirmed."
    )


def test_generate_report_defaults_to_advanced_diagnosis():
    incident = load_incident(14)
    report = generate_report(incident)
    expected = diagnose_advanced(incident)
    verification = verify(incident, expected)

    assert report["diagnosis"] == expected
    assert report["verified"] == verification["verified"]
    assert report["confidence"] == verification["confidence"]
    assert report["competing_patterns"] == verification["competing_patterns"]


def test_recommendations_never_exceed_four_lines():
    with INCIDENTS_PATH.open(encoding="utf-8") as file:
        incidents = json.load(file)

    for incident in incidents:
        report = generate_report(incident)
        assert len(report["recommendations"]) <= 4
        assert report["safety_note"] == SAFETY_NOTE


def test_format_report_includes_required_sections():
    incident = load_incident(1)
    text = format_report(generate_report(incident))

    assert "Incident Report" in text
    assert "Service: checkout-api" in text
    assert "Diagnosis: database_latency" in text
    assert "Confidence: high" in text
    assert SAFETY_NOTE in text
    assert text.strip().endswith(SAFETY_NOTE)


def test_report_is_deterministic():
    incident = load_incident(10)
    first = generate_report(incident)
    second = generate_report(incident)
    assert first == second
    assert format_report(first) == format_report(second)
