# 03 — Independent verifier

## Goal

Check whether a claimed diagnosis is actually supported by telemetry, including cases that are correct but not unique, without changing the diagnosis or expected labels.

## Git

- `a429c05` — add verifier reliability tests (`verifier.py`, `tests/test_verifier.py`)

Not modified: `baseline.py`, `advanced.py`, `evaluate.py`, `evaluate_advanced.py`, `data/incidents.json`, expected-cause labels.

## What landed

`verify(incident, diagnosis)` independently checks complete-pattern evidence. It does not read expected labels, does not rewrite the diagnosis, and does not remediate.

Return shape:

```python
{
    "diagnosis": "traffic_spike",
    "verified": True,
    "evidence": [...],
    "confidence": "medium",
    "competing_patterns": ["database_latency"]
}
```

Confidence: high if the pattern is complete and unique; medium if complete but another abnormal pattern is also complete; low if not complete (including unknown diagnoses).

## Result (advanced diagnoses on the frozen set)

```text
15/15 diagnoses verified
High confidence:   14
Medium confidence:  1
Low confidence:     0
```

The medium case is **case 10** (`reporting-api`): verified `traffic_spike` with competing pattern `database_latency`.

## Reliability tests (`tests/test_verifier.py`)

- unsupported CPU diagnosis rejected (case 14, high CPU, healthy latency)
- unsupported traffic diagnosis rejected (case 13, high traffic, healthy latency)
- unknown diagnosis rejected (`mystery_cause`)
- supported database diagnosis verified (case 1, high confidence)
- ambiguous case 10 detected (`traffic_spike` verified, competitor `database_latency`)

## Roles

**Cursor.** Implemented `verifier.py` and the five reliability tests; evaluation confirmed 15/15 verified with 14 high / 1 medium.

**ChatGPT.** Review/advice that 100% classification accuracy is not the same as unique supporting evidence, so verification should be a separate layer.

**Human.** Approved an independent verifier that cannot change diagnoses or production systems. Required negative tests for unsupported and unknown diagnoses. Confirmed case 10 should surface `database_latency` rather than hide it.
