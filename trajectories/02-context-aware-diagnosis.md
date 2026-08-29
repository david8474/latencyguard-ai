# 02 — Context-aware diagnosis

## Goal

Raise diagnosis accuracy on the same frozen 15 cases by using metric relationships, without changing the baseline or expected labels.

## Git

- `e19ca4c` — add context-aware latency diagnosis iteration (`advanced.py`, `evaluate_advanced.py`)

Not modified: `baseline.py`, `evaluate.py`, `data/incidents.json`, expected-cause labels.

## What landed

`diagnose_advanced` keeps deterministic rules but adds context:

- request rate relative to `baseline_request_rate` (traffic spike at ≥ 2.0× when latency is elevated)
- elevated latency as p95 ≥ 500 ms or p99 ≥ 1500 ms
- CPU/memory/DB diagnoses only when those signals are high **and** latency is elevated
- application errors still gated on error rate
- tail-latency pattern unchanged in form (high p99, healthy p95)
- otherwise `normal`

Example that the baseline missed: reporting-api case 10, `980 / 400 = 2.45×` baseline with elevated p95/p99. The baseline treated `980 < 1000` as normal.

## Result

```text
Baseline:  9/15  = 60.0%
Advanced: 15/15 = 100.0%

Improvement: +40 percentage points
Regressions: 0
```

All six baseline failures were corrected. Cases 13 and 14 stay `normal` because high request rate or CPU without elevated latency is not treated as user-facing degradation.

## Roles

**Cursor.** Implemented `advanced.py` and `evaluate_advanced.py` and evaluated against the frozen set.

**ChatGPT.** Review/advice that isolated thresholds were the main failure mode and that relative traffic plus latency correlation were the minimum contextual fixes.

**Human.** Approved a separate advanced path instead of editing the baseline. Kept the evaluation set frozen. After 15/15 with 0 regressions, decided this iteration was enough for classification and did not add an LLM or ML runtime for diagnosis.
