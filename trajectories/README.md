# Development Trajectories

These notes record the representative AI-assisted development path of LatencyGuard AI.

They are based on git history, the frozen 15-case evaluation set in `data/incidents.json`, measured evaluation and test results, the project README, and Cursor/human checkpoints that are part of this repository’s history.

They do **not** reproduce full ChatGPT transcripts. ChatGPT was used for review and advice; Cursor implemented and evaluated code in the repo; human approval decided what landed.

## Roles

| Role | What it did |
|---|---|
| **Cursor** | Implemented and evaluated in-repo code: baseline, context-aware diagnosis, verifier, report layer, and pytest runs. |
| **ChatGPT** | Review and advice on problem framing, iteration design, and interpretation of results. Not used as a runtime model. |
| **Human** | Froze the evaluation set and labels, approved each iteration, kept the baseline unchanged, forbade automatic remediation, and decided not to add an LLM/ML runtime after the deterministic system hit the target results. |

## Timeline

| File | Stage | Git checkpoint | Result |
|---|---|---|---|
| [01-baseline-analysis.md](01-baseline-analysis.md) | Baseline | `52479cf`, `6943720` | 9/15 = 60% |
| [02-context-aware-diagnosis.md](02-context-aware-diagnosis.md) | Iteration 1 | `e19ca4c` | 15/15 = 100%, 0 regressions |
| [03-verifier.md](03-verifier.md) | Iteration 2 | `a429c05` | 15/15 verified; 14 high, 1 medium |
| [04-report-layer.md](04-report-layer.md) | Final | `e0dea6a` | evidence-backed reports; 14 tests passed |

## Verified final results

- Baseline: 9/15 correct (60.0%)
- Context-aware diagnosis: 15/15 correct (100.0%), 0 regressions
- Independent verification: 15/15 verified; 14 high, 1 medium, 0 low
- Case 10 competing pattern: `database_latency`
- Final pytest suite: 14 passed
- Runtime: deterministic Python; no LLM, ML model, or API key
