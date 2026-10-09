# ADR 0001 — Pure analysis core, CPU-only CI

## Status
Accepted.

## Context
LLM serving benchmarks need a GPU and a running inference server. If the whole
project required that, nobody could run the tests, CI could not be green, and a
reviewer could not verify correctness without renting a GPU.

## Decision
Split the project into two halves:

- **Analysis core** (`workload`, `metrics`, `cost`, `slo`, `quantization`,
  `report`, `runner` + `clients/mock`): pure Python, deterministic, no network,
  no GPU. This is the logic that is easy to get subtly wrong — percentile maths,
  TPOT definition, cost per 1M tokens, SLO gating, regression detection — so it is
  fully unit-tested and runs in CI on CPU.
- **Live layer** (`clients/openai_compat`, `scripts/serve_*.sh`,
  `scripts/run_bench.py` live mode, `monitoring/`): drives real vLLM / TGI
  servers. Exercised by hand on a GPU box, not in CI.

A `MockEngine` simulates prefill + decode service times and a queueing simulation
turns arrivals + concurrency into a makespan, so the full pipeline produces a
realistic sample report with zero infrastructure.

## Consequences
- Green CI is honest: it proves the maths, not a fake server.
- The simulator is clearly labelled a simulation, never presented as measurement.
- Live numbers belong in `docs/RESULTS_TEMPLATE.md`, generated on real hardware.
