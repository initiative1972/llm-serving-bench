# Results — <model>, <GPU>, <date>

> Fill this in from **live** runs on real hardware. The numbers below are an
> example shape only. Keep the "measured vs simulated" line honest.

**Setup:** model `<org/model>`, GPU `<e.g. 1x A100-80GB>`, engine `<vLLM 0.x / TGI 2.x>`,
`max-model-len 8192`, workload `chat` (prompt≈256, output≈256), Poisson @ 20 req/s,
500 requests, concurrency 32. Mode: **measured** (not simulated).

## Latency, throughput, cost

| Config | TTFT p90 (ms) | TPOT p90 (ms) | E2E p99 (ms) | Throughput (req/s) | Out tok/s | A$/1M tok | SLO |
|---|---|---|---|---|---|---|---|
| vllm-fp16 | 180 | 11.0 | 5,900 | 22.4 | 1,180 | 1.12 | PASS |
| vllm-awq  | 150 | 9.5  | 5,100 | 27.1 | 1,460 | 0.91 | PASS |
| tgi-gptq  | 210 | 12.3 | 6,800 | 19.8 | 1,040 | 1.27 | PASS |

## VRAM fit (from `src/quantization.py`)

| Format | 7B weights (GB) | Est. serving VRAM (GB) | Fits 24 GB? |
|---|---|---|---|
| fp16 | 13.0 | ~17.3 | yes |
| awq  | 3.3  | ~6.1  | yes |

## Read-out
- **Pick:** `<which config and why>` — e.g. AWQ wins on cost/token and TTFT with no
  SLO breach; FP16 kept as the quality baseline.
- **Headroom:** `<closest SLO and how close>`.
- **Caveats:** quality was/was not evaluated separately (benchmark measures speed
  and cost, not answer quality — see roadmap).
