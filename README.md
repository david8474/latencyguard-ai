# LatencyGuard AI

LatencyGuard AI is a deterministic incident-triage system for backend, DevOps, and SRE workflows.

It analyzes p95/p99 latency, CPU, memory, database latency, error rate, and request traffic to identify likely causes of service degradation, verify the diagnosis, and generate evidence-backed investigation steps.

## Results

| Version | Result |
|---|---:|
| Baseline | 9/15 correct (60.0%) |
| Context-Aware Diagnosis | 15/15 correct (100.0%) |
| Independent Verification | 15/15 verified |
| Confidence | 14 high, 1 medium, 0 low |
| Final Test Suite | 14 tests passed |

**Primary improvement: 60% → 100% accuracy (+40 percentage points).**

---

## Problem

Fixed monitoring thresholds can miss service-specific anomalies or create false positives.

For example, 980 requests/sec may appear normal under a 1000 req/s threshold. But if the service normally handles 400 req/s, traffic is actually **2.45x baseline**.

LatencyGuard AI uses telemetry context and relationships between metrics rather than relying only on isolated thresholds.

---

## Architecture

```text
Service Telemetry
       ↓
Context-Aware Diagnosis
     advanced.py
       ↓
Likely Cause
       ↓
Independent Verification
     verifier.py
       ↓
Evidence + Confidence
       ↓
Incident Triage Report
      report.py
       ↓
Human Engineer
```

The system does **not** automatically modify production systems.

---

## What It Diagnoses

LatencyGuard AI detects:

- `database_latency`
- `cpu_saturation`
- `traffic_spike`
- `memory_pressure`
- `application_errors`
- `tail_latency_anomaly`
- `normal`

Telemetry includes:

```json
{
  "service": "reporting-api",
  "p95_ms": 1050,
  "p99_ms": 2800,
  "cpu_percent": 79,
  "memory_percent": 74,
  "db_latency_ms": 720,
  "error_rate": 0.02,
  "request_rate": 980,
  "baseline_request_rate": 400
}
```

---

## Baseline

The baseline uses simple absolute thresholds for CPU, traffic, memory, database latency, and errors.

### Result

```text
9/15 correct = 60.0%
```

Six cases failed because absolute thresholds either missed contextual anomalies or produced false positives.

Examples:

- relative traffic spikes were missed
- moderate database degradation was missed
- high traffic with healthy latency was incorrectly classified
- high CPU with healthy latency was incorrectly classified

**Main learning:** isolated metrics are not always enough to determine user-facing degradation.

---

## Iteration 1 — Context-Aware Diagnosis

`advanced.py` adds relationships between telemetry signals, including:

- request rate relative to service baseline
- p95/p99 degradation
- CPU correlated with latency
- database latency correlated with application latency
- memory pressure with latency
- tail-latency patterns

Example:

```text
request_rate = 980
baseline_request_rate = 400

980 / 400 = 2.45x baseline
```

The baseline missed this because `980 < 1000`. The advanced version recognizes the relative traffic anomaly when latency is also degraded.

### Result

```text
Baseline:  9/15  = 60.0%
Advanced: 15/15 = 100.0%

Improvement: +40 percentage points
Regressions: 0
```

---

## Iteration 2 — Independent Verification

A correct classification does not guarantee that the telemetry strongly or uniquely supports it.

`verifier.py` independently checks the claimed diagnosis and returns:

```python
{
    "diagnosis": "traffic_spike",
    "verified": True,
    "evidence": [...],
    "confidence": "medium",
    "competing_patterns": ["database_latency"]
}
```

The verifier does not read expected labels, change the diagnosis, or perform remediation.

### Result

```text
15/15 diagnoses verified

High confidence:   14
Medium confidence:  1
Low confidence:     0
```

Tests also confirm that unsupported CPU/traffic diagnoses and unknown labels are rejected.

---

## Handling Ambiguity

Case 10 demonstrates why verification is useful:

```text
Service: reporting-api
Request rate: 980
Baseline: 400
Traffic ratio: 2.45x
p95: 1050 ms
p99: 2800 ms
DB latency: 720 ms
```

Result:

```text
Diagnosis: traffic_spike
Verified: yes
Confidence: medium
Competing pattern: database_latency
```

Instead of pretending there is only one possible cause, LatencyGuard AI surfaces the competing database pattern for human investigation.

---

## Final Iteration — Incident Reports

`report.py` turns the diagnosis and verification result into a concise SRE/DevOps incident report.

Example:

```text
Service: reporting-api
Diagnosis: traffic_spike
Verified: yes
Confidence: medium
Competing patterns: database_latency

Evidence:
- request rate is 2.45x baseline
- p95/p99 latency is elevated

Recommended investigation:
- Investigate database latency as a competing cause.
- Confirm request rate versus baseline.
- Identify the source of additional traffic.
- Review whether latency increased with traffic.

No production changes were automatically performed.
```

This gives engineers a diagnosis, evidence, confidence level, ambiguity warning, and investigation steps.

---

## Improvement Changelog

| Stage | Change | Result |
|---|---|---|
| Baseline | Absolute threshold rules | 60% accuracy |
| Iteration 1 | Added contextual/relational telemetry reasoning | 100% accuracy |
| Iteration 2 | Added independent evidence verification | 15/15 verified |
| Final | Added human-readable incident reports | Evidence + investigation steps |

All improvements were kept because they produced measurable value without adding unnecessary runtime complexity.

---

## Final Comparison

| Capability | Baseline | Final |
|---|---|---|
| Service baseline context | No | Yes |
| Relative traffic analysis | No | Yes |
| Latency correlation | No | Yes |
| Independent verification | No | Yes |
| Confidence scoring | No | Yes |
| Competing-cause detection | No | Yes |
| Evidence | No | Yes |
| Investigation recommendations | No | Yes |
| Automatic production changes | No | No |
| Accuracy | **60%** | **100%** |

---

## Main Failure Mode / Hot Take

The baseline's biggest weakness was **lack of context**.

High CPU or traffic alone does not necessarily indicate an incident, while a metric below a global threshold may still be abnormal for a specific service.

**Hot take:** more sophisticated models are not automatically better. For this focused problem, deterministic contextual reasoning plus independent verification is easier to test, reproduce, audit, and explain than adding an unnecessary LLM or ML dependency.

---

## Reproduction Guide

### Requirements

- Python 3
- Git
- pytest

No API key or external AI service is required.

### Clone

```bash
git clone https://github.com/david8474/latencyguard-ai.git
cd latencyguard-ai
```

### Install pytest

```bash
python -m pip install pytest
```

### Run baseline

```bash
python evaluate.py
```

Expected:

```text
Accuracy: 9/15 (60.0%)
```

### Run advanced evaluation

```bash
python evaluate_advanced.py
```

Expected:

```text
Accuracy: 15/15 (100.0%)
```

### Run tests

```bash
python -m pytest -v
```

Expected:

```text
14 passed
```

---

## Project Structure

```text
latencyguard-ai/
├── baseline.py
├── advanced.py
├── verifier.py
├── report.py
├── evaluate.py
├── evaluate_advanced.py
├── data/
│   └── incidents.json
└── tests/
    ├── test_verifier.py
    └── test_report.py
```

---

## Evaluation

The primary metric is:

```text
correct diagnoses / total incidents
```

Both baseline and advanced versions use the same frozen 15-case evaluation set.

The baseline implementation and expected labels remain unchanged during advanced development.

Verification is evaluated separately from classification accuracy.

---

## Safety and Human Control

LatencyGuard AI is a **triage assistant**, not an autonomous remediation system.

It can analyze telemetry, identify likely causes, verify evidence, surface ambiguity, and recommend investigation steps.

It does **not** restart services, modify infrastructure, deploy code, change databases, or automatically remediate incidents.

Consequential actions remain under human control.

---

## Agent / Development Trajectories

The project was developed with AI-assisted engineering using **ChatGPT and Cursor**.

Representative trajectories include:

1. baseline analysis and evaluation
2. context-aware diagnosis design
3. independent verifier design
4. negative reliability testing
5. incident-report design
6. human approval and evaluation checkpoints

These trajectories document the prompts, reasoning, revisions, and measured results that led from the 60% baseline to the final system.

---

## Technologies

- Python
- pytest
- Git / GitHub
- Cursor
- ChatGPT

The final runtime is deterministic and requires **no LLM, external model, or API key**.

---

## Conclusion

LatencyGuard AI improved root-cause diagnosis from **60% to 100%** while adding independent verification, confidence scoring, competing-cause detection, and evidence-backed investigation recommendations.

The key lesson: for a focused operational problem, **context, verification, and measurement can provide more value than unnecessary model complexity.**
