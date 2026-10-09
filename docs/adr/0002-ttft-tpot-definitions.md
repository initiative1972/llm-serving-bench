# ADR 0002 — Latency definitions (TTFT, TPOT, E2E)

## Status
Accepted.

## Context
"Latency" is ambiguous for streaming LLMs. A single number hides the two things
users actually feel: how long until the first token appears, and how fast tokens
then stream. Comparing engines on a single average is misleading.

## Decision
Measure three things per request and report percentiles (p50/p90/p95/p99), not
just means:

- **TTFT (time to first token)** — dispatch to first streamed token. Dominated by
  queueing + prefill. This is the "feel" of responsiveness.
- **TPOT (time per output token)** — decode-phase cost, computed as
  `(end_to_end - TTFT) / (output_tokens - 1)`. Governs streaming speed.
- **E2E (end-to-end)** — dispatch to final token.

Throughput is reported separately as requests/second and output tokens/second over
wall-clock, because a config can have great per-request latency and poor aggregate
throughput (or vice versa) depending on batching.

## Consequences
- Decisions are made on the dimension that matters for the workload (interactive
  chat weights TTFT; batch generation weights tokens/second).
- TPOT needs `output_tokens >= 2`; otherwise it is reported as null, not zero.
