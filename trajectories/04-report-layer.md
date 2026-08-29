# 04 — Incident report layer

## Goal

Turn diagnosis plus verification into a concise, evidence-backed investigation report for a human engineer. No CLI, dashboard, or automatic remediation.

## Git

- `e0dea6a` — add evidence-backed incident triage reports (`report.py`, `tests/test_report.py`)

Not modified: `baseline.py`, `advanced.py`, `verifier.py`, `evaluate.py`, `evaluate_advanced.py`, `data/incidents.json`, expected-cause labels.

## Human-approved constraints (then implemented)

The report layer was approved before implementation, with these requirements:

- deterministic and dependency-free
- safety note exactly: `No production changes were automatically performed.`
- no automatic production remediation
- medium confidence must surface the competing cause before diagnosis-specific investigation steps
- low/unverified diagnoses must say they are not confirmed
- recommendations at most 4 lines

## What landed

`generate_report` uses `diagnose_advanced` by default, then `verify`. `format_report` prints ID, service, diagnosis, verified, confidence, competing patterns, summary, evidence, investigation steps, and the safety note.

## Measured checks

Final pytest suite: **14 passed** (`tests/test_verifier.py` + `tests/test_report.py`).

Generated reports for cases 1, 10, and 14:

- Case 1: verified `database_latency`, high confidence, no competing patterns
- Case 10: verified `traffic_spike`, medium confidence, competing `database_latency` listed first in recommendations
- Case 14 (default advanced diagnosis): verified `normal`, high confidence (CPU high, latency healthy)

Forcing `diagnosis="cpu_saturation"` on case 14 yields unverified / low confidence and the wording that the diagnosis is not confirmed.

## Decision not to add LLM/ML at runtime

After 15/15 accuracy, 15/15 verified diagnoses, and 14 passing tests, the human decision was **not** to add an LLM or ML runtime dependency. Diagnosis, verification, and reporting stay deterministic Python with no API key.

## Roles

**Cursor.** Implemented `report.py` and `tests/test_report.py` to the approved spec, ran the full pytest suite (14 passed), and generated the case 1 / 10 / 14 reports.

**ChatGPT.** Review/advice that the last layer should be a human-readable triage report (evidence, confidence, competing cause, investigation steps), not autonomous remediation.

**Human.** Approved the spec, including the exact safety note and the ban on production changes. Chose not to add a CLI, dashboard, or LLM/ML runtime after the deterministic system met the target results.
