"""Benchmark orchestration.

Simulation mode (CPU / CI): a ``MockEngine`` produces per-request service times,
and a simple C-worker queueing simulation turns arrival times + concurrency into a
wall-clock makespan and a scheduled start/end per request. Fully deterministic and
unit-tested — no GPU, no server.

Live mode (GPU, not run in CI): see ``scripts/run_bench.py``, which drives the
OpenAI-compatible client against a running vLLM / TGI server.
"""
from __future__ import annotations

import heapq
from dataclasses import dataclass

from . import metrics as m
from .clients.base import RequestResult


@dataclass
class RunResult:
    results: list
    wall_time: float
    concurrency: int


def simulate(engine, specs, concurrency=1):
    """Run a C-worker queue simulation; return a :class:`RunResult`."""
    if concurrency < 1:
        raise ValueError("concurrency must be >= 1")
    services = {s.request_id: engine.service(s) for s in specs}
    order = sorted(specs, key=lambda s: s.arrival_time)
    free = [0.0] * concurrency  # min-heap of per-worker "free at" times
    heapq.heapify(free)
    scheduled = []
    wall = 0.0
    for spec in order:
        worker_free = heapq.heappop(free)
        start = max(spec.arrival_time, worker_free)
        svc = services[spec.request_id]
        end = start + svc.latency
        heapq.heappush(free, end)
        wall = max(wall, end)
        scheduled.append(RequestResult(
            request_id=spec.request_id,
            prompt_tokens=svc.prompt_tokens,
            output_tokens=svc.output_tokens,
            start_time=start,
            end_time=end,
            ttft=svc.ttft,
            success=svc.success,
            error=svc.error,
        ))
    return RunResult(results=scheduled, wall_time=wall, concurrency=concurrency)


def summarise(run):
    """Aggregate a :class:`RunResult` into the metrics dict."""
    return m.aggregate([r.to_record() for r in run.results], run.wall_time)
