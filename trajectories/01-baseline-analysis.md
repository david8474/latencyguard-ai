# 01 — Baseline analysis

## Goal

Measure a simple, inspectable diagnosis baseline on a frozen incident set before adding contextual rules.

## Git

- `52479cf` — record baseline with service traffic context (`baseline.py`, `evaluate.py`, initial `data/incidents.json`)
- `6943720` — freeze 15-case evaluation and final baseline (evaluation set expanded to 15 cases)

`baseline.py` and expected-cause labels were not changed in later iterations.

## What landed

`diagnose_baseline` uses isolated absolute thresholds:

- CPU ≥ 90% → `cpu_saturation`
- DB latency ≥ 800 ms → `database_latency`
- error rate ≥ 0.10 → `application_errors`
- memory ≥ 90% → `memory_pressure`
- request rate ≥ 1000 → `traffic_spike`
- p99 ≥ 1500 ms and p95 < 500 ms → `tail_latency_anomaly`
- otherwise → `normal`

Service `baseline_request_rate` is present in the data but unused by the baseline.

## Result

```text
9/15 correct = 60.0%
```

The six failures on the frozen set:

| Case | Service | Expected | Baseline predicted |
|---|---|---|---|
| 10 | reporting-api | `traffic_spike` | `normal` |
| 11 | checkout-worker | `traffic_spike` | `normal` |
| 12 | customer-api | `database_latency` | `normal` |
| 13 | media-api | `normal` | `traffic_spike` |
| 14 | notification-api | `normal` | `cpu_saturation` |
| 15 | analytics-api | `traffic_spike` | `normal` |

These match the documented failure modes: relative traffic spikes missed (`980 < 1000` while 2.45× the service baseline), moderate DB degradation missed (`760 < 800`), and high traffic or CPU with healthy latency classified as incidents.

## Roles

**Cursor.** Implemented `baseline.py` and `evaluate.py`, recorded the incident set, and ran evaluation.

**ChatGPT.** Review/advice on treating this as a measured baseline (absolute thresholds, frozen labels) rather than jumping to a more complex model.

**Human.** Froze the 15-case set and expected labels. Required later work to keep `baseline.py` and labels unchanged so improvement could be compared against this 60% result.
