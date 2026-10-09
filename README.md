# llm-serving-bench
A reproducible benchmark + cost harness for self-hosted LLM inference.  Compare
serving engines (**vLLM**, **TGI**) and **quantisation** formats (FP16/BF16, FP8,
AWQ, GPTQ, GGUF, INT8) on **latency** (TTFT / TPOT / E2E percentiles),
**throughput** (req/s, tokens/s), and **cost** (A$/1M tokens, A$/1k requests) —
then gate the result against an **SLO + budget** and watch it live in
**Prometheus + Grafana**.

> **Why this exists.** Picking how to serve an open-weight model is an engineering
> trade-off: quality vs latency vs throughput vs VRAM vs dollars. This repo turns
> that into numbers you can defend — and bakes the decision into a pass/fail gate.

![CI](https://img.shields.io/badge/CI-flake8%20%2B%20pytest-brightgreen)
![python](https://img.shields.io/badge/python-3.11%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)

---

## The one idea that makes this credible

Benchmarking LLMs needs a GPU and a live server. So the project is split in two:

| Layer | What | Runs where |
|---|---|---|
| **Analysis core** | workload gen · latency/throughput maths · cost model · SLO gate · VRAM fit · regression detection · reporting | **CPU, in CI** — pure functions, fully unit-tested |
| **Live layer** | vLLM/TGI launch scripts · async streaming load client · Prometheus/Grafana | **GPU box**, by hand |

A built-in **CPU simulator** (`MockEngine` + a queueing simulation) runs the entire
pipeline — workload → results → metrics → cost → SLO → report — with **no GPU and no
server**, so anyone (including CI) can produce a sample report. It is always labelled
a *simulation*, never passed off as a measurement.

This is the honesty line the repo holds throughout: **the maths is tested and
inspectable; real throughput numbers come from real hardware and live in
`docs/RESULTS_TEMPLATE.md`.**

---

## Quickstart (no GPU required)

```bash
python -m pip install -r requirements-dev.txt     # pytest + flake8
python -m pytest -q                               # all tests green on CPU
python -m flake8 src tests scripts                # clean

# generate a sample report with the simulator
python scripts/run_bench.py --simulate --profile chat --n 300 --concurrency 16 --name demo
```

> On this Windows machine the Python launcher is `py`, e.g. `py -m pytest -q` and
> `py scripts/run_bench.py --simulate ...`.

Output is a markdown comparison table plus a PASS/FAIL against the SLO, written to
`reports/`.

## Run it for real (GPU)

```bash
# 1) start an engine (pick one)
MODEL=TheBloke/Mistral-7B-Instruct-v0.2-AWQ QUANT=awq bash scripts/serve_vllm.sh
MODEL=TheBloke/Mistral-7B-Instruct-v0.2-GPTQ QUANT=gptq bash scripts/serve_tgi.sh

# 2) benchmark it (TTFT captured from the first streamed token)
python scripts/run_bench.py --base-url http://localhost:8000 --model <model> \
    --profile chat --n 500 --concurrency 32 --rate 20 --pattern poisson --name vllm-awq

# 3) watch it live
docker compose -f monitoring/docker-compose.yml up -d   # Grafana on :3000
```

Record the results in `docs/RESULTS_TEMPLATE.md`.

---

## What it measures (and why those metrics)

- **TTFT** (time to first token) — responsiveness; dominated by queueing + prefill.
- **TPOT** (time per output token) — streaming speed; `(E2E − TTFT) / (out − 1)`.
- **E2E** — full request latency.
- **Throughput** — requests/second and output tokens/second over wall-clock.
- **Cost** — `A$/1M output tokens = (hourly_AUD/3600) / out_tok_per_s × 1e6`.
- **VRAM fit** — will this model+quant fit the card with room for KV cache?

Percentiles (p50/p90/p95/p99), not just means — because tail latency is the SLO.
See `docs/adr/` for the reasoning on each (CPU-only CI, latency definitions, cost
model).

## Quantisation at a glance (`src/quantization.py`)

| Format | Bits | Bytes/param | Note |
|---|---|---|---|
| fp16 / bf16 | 16 | 2.0 | Quality baseline |
| fp8 / int8 | 8 | 1.0 | ~half the weight VRAM |
| awq / gptq | 4 | 0.5 | 4-bit weight-only; strong quality retention |
| gguf_q4_k_m | ~4.5 | 0.56 | llama.cpp k-quant; CPU/edge |

`estimate_vram_gb(7, "awq")` ≈ 6 GB → fits a 24 GB card with KV-cache headroom;
`fits(70, "fp16", 24)` is `False`. Decisions are made on **cost per token**, not
just "does it fit".

---

## Project layout

```
src/
  workload.py        synthetic request generation (len distributions + arrivals)
  metrics.py         percentiles, throughput, token rates
  cost.py            GPU price -> A$/1M tokens, A$/1k requests
  slo.py             SLO definition + pass/fail + headroom
  quantization.py    format metadata + VRAM-fit estimation
  report.py          comparison table + regression gate
  runner.py          queueing simulation (CPU) orchestration
  clients/
    base.py          RequestResult (TTFT/TPOT/E2E derivations)
    mock.py          deterministic simulation engine (CI)
    openai_compat.py async streaming client for vLLM/TGI (live)
scripts/             serve_vllm.sh · serve_tgi.sh · run_bench.py
monitoring/          Prometheus + Grafana + DCGM GPU exporter
config/              engines.yaml · workloads.yaml · slo.yaml
  tests/               34 unit tests (CPU, no GPU)
docs/                ADRs + RESULTS_TEMPLATE.md
```

## Testing & CI

GitHub Actions (Python 3.11) runs **flake8 + pytest** and a **simulator smoke test**
on every push — all on CPU, no GPU, no secrets. The green badge means the analysis
logic is correct, not that a server was faked.

## Honesty & scope

- All data is **synthetic**; the simulator is a simulation, clearly marked.
- GPU prices and the FX rate are **illustrative inputs**, not quotes — override them.
- This harness measures **speed and cost, not answer quality**. Pair it with an
  eval suite (see the companion `domain-llm-finetune` repo) before concluding a
  quantised model is "good enough".
- Live numbers belong in `docs/RESULTS_TEMPLATE.md`, produced on real hardware.

## Roadmap

- Add a quality gate (hook an eval harness so cost/latency is traded against
  accuracy, not measured in isolation).
- Triton / TensorRT-LLM client; speculative decoding and prefix-caching sweeps.
- Automatic Pareto frontier (latency × cost × quality) across configs.
- CI regression gate using `report.detect_regressions` against a stored baseline.

## License

MIT © 2026 Henry Yan.
