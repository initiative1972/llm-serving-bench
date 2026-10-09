# run_bench.py

```python
#!/usr/bin/env python
"""
CLI benchmark runner.

Default is SIMULATION mode (no GPU / server) so anyone can produce a sample report:
    py scripts/run_bench.py --simulate --profile chat --n 300 --concurrency 16

Live mode drives an OpenAI-compatible server (vLLM / TGI):
    py scripts/run_bench.py --base-url http://localhost:8000 --model my-model \
        --profile chat --n 500 --concurrency 32 --rate 20 --pattern poisson
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time

# Allow `python scripts/run_bench.py` from the repo root to import the `src` pkg.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import cost as costmod  # noqa: E402
from src import metrics as m  # noqa: E402
from src import report as reportmod  # noqa: E402
from src import slo as slomod  # noqa: E402
from src.clients.mock import MockEngine  # noqa: E402
from src.runner import simulate  # noqa: E402
from src.workload import generate_requests  # noqa: E402


def _parse():
    ap = argparse.ArgumentParser(description="LLM serving benchmark")

    ap.add_argument(
        "--simulate",
        action="store_true",
        help="run the CPU simulator (no GPU/server)"
    )

    ap.add_argument(
        "--base-url",
        default=None,
        help="OpenAI-compatible server, e.g. http://localhost:8000"
    )

    ap.add_argument("--model", default="model")

    ap.add_argument(
        "--endpoint",
        default="chat",
        choices=["chat", "completions"]
    )

    ap.add_argument("--profile", default="chat")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--rate", type=float, default=0.0)

    ap.add_argument(
        "--pattern",
        default="offline",
        choices=["offline", "uniform", "poisson"]
    )

    ap.add_argument("--gpu", default="A100-80GB")
    ap.add_argument("--name", default="run")
    ap.add_argument("--out", default="reports/bench.md")

    return ap.parse_args()


async def _run_live(args, specs):
    from src.clients.openai_compat import OpenAICompatClient

    client = OpenAICompatClient(
        args.base_url,
        args.model,
        endpoint=args.endpoint
    )

    sem = asyncio.Semaphore(args.concurrency)
    t_start = time.perf_counter()

    async def _one(spec):
        delay = spec.arrival_time - (time.perf_counter() - t_start)

        if delay > 0:
            await asyncio.sleep(delay)

        async with sem:
            return await client.arun(
                spec,
                start_offset=spec.arrival_time
            )

    results = await asyncio.gather(*[_one(s) for s in specs])
 *  wall = time.perf_counter() - t_s*art

    return list(results), wal*


def main():
    args = _parse()*
    specs = generate_requests(
  *     args.n,
        profile=args.*rofile,
        rate=args.rate,
  *     pattern=args.pattern
    )

 *  if args.simulate or not args.bas*_url:
        run = simulate(
    *       MockEngine(name=args.name),*            specs,
            con*urrency=args.concurrency
        )*
        results = [r.to_record() *or r in run.results]
        wall * run.wall_time
        mode = "SIM*LATION"

    else:
        res_obj*, wall = asyncio.run(_run_live(arg*, specs))
        results = [r.to_record() for r in res_objs]
       *mode = "LIVE"

    met = m.aggrega*e(results, wall)

    cm = costmod*CostModel(gpu=args.gpu)
    aud = *m.aud_per_1m_output_tokens(
      * met["output_tokens_per_s"]
    )
*    slo = slomod.SLO(
        ttft*p90_ms=500,
        e2e_p99_ms=800*,
        min_throughput_rps=1.0
 *  )

    ev = slomod.evaluate(
   *    met,
        slo,
        aud_*er_1m_tokens=aud
    )

    runs =*[{
        "name": args.name,
        "metrics": met,
        "aud_per_1m": aud,
        "slo_passed": ev["passed"]
    }]

    path = repo*tmod.write_report(
        runs,
 *      args.out,
        title=f"LL* serving benchmark — {args.name} [{mode}]"
    )

    print(reportmod*to_markdown(runs))
    print(f"\nm*de: {mode}  |  SLO passed: {ev['passed']}")
    print(f"report: {path*")


if __name__ == "__main__":
  * main()