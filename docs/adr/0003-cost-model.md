# ADR 0003 — Cost model: price per token, not price per hour

## Status
Accepted.

## Context
GPU hourly price alone does not tell you whether a serving config is economical.
A cheaper GPU that produces far fewer tokens/second can be more expensive per unit
of useful work. The question a business asks is "what does 1M tokens cost?"

## Decision
Convert throughput into unit economics:

```
A$ / 1M output tokens = (hourly_AUD / 3600) / output_tokens_per_second * 1e6
```

- Prices in `cost.py` are **illustrative public list prices** and clearly marked
  as such; real runs should pass the provider's actual `usd_per_hr`.
- Report both `A$/1M tokens` and `A$/1k requests`, because mixed input/output
  lengths make one or the other the more honest denominator per workload.
- Cost is an SLO dimension (`max_aud_per_1m_tokens`), so a config can pass on
  latency and still be rejected on budget — which is the real-world trade-off.

## Consequences
- Quantisation choices (AWQ/GPTQ vs FP16) are compared on cost per token, not just
  on whether they fit in VRAM.
- FX and prices drift; they are inputs, never hard-coded into the conclusions.
