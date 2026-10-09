"""Synthetic workload generation for LLM serving benchmarks.

Pure functions: given a workload profile and a seed, produce a deterministic list
of request specs (prompt / output token counts + arrival times). No network and no
model — this is what lets the benchmark harness be unit-tested on CPU in CI.
"""
from __future__ import annotations

import math
import random
from dataclasses import dataclass


@dataclass(frozen=True)
class RequestSpec:
    request_id: str
    prompt_tokens: int
    max_output_tokens: int
    arrival_time: float  # seconds since benchmark start


# Illustrative workload profiles (mean token counts + coefficient of variation).
PROFILES = {
    "chat":      {"prompt": 256,  "output": 256,  "cv": 0.5},
    "rag":       {"prompt": 2048, "output": 300,  "cv": 0.4},
    "summarise": {"prompt": 3072, "output": 512,  "cv": 0.3},
    "batch_gen": {"prompt": 512,  "output": 1024, "cv": 0.6},
}


def _lognormal_int(rng, mean, cv, lo=1):
    """Draw a positive integer around ``mean`` with coefficient of variation ``cv``."""
    if cv <= 0:
        return max(lo, int(round(mean)))
    sigma = math.sqrt(math.log(1 + cv * cv))
    mu = math.log(mean) - 0.5 * sigma * sigma
    val = int(round(rng.lognormvariate(mu, sigma)))
    return max(lo, val)


def _arrivals(rng, n, rate, pattern):
    if pattern == "offline" or rate <= 0:
        return [0.0] * n
    if pattern == "uniform":
        step = 1.0 / rate
        return [i * step for i in range(n)]
    if pattern == "poisson":
        t = 0.0
        out = []
        for _ in range(n):
            t += rng.expovariate(rate)
            out.append(t)
        return out
    raise ValueError(f"unknown arrival pattern: {pattern}")


def generate_requests(n, profile="chat", rate=0.0, pattern="offline",
                      seed=1234, prompt_tokens=None, output_tokens=None):
    """Return a deterministic list of :class:`RequestSpec`.

    ``rate`` (req/s) drives the arrival process; ``pattern`` is one of
    offline | uniform | poisson. ``prompt_tokens`` / ``output_tokens`` override the
    profile means when provided.
    """
    if profile not in PROFILES:
        raise ValueError(f"unknown profile: {profile}")
    p = PROFILES[profile]
    mean_prompt = prompt_tokens if prompt_tokens is not None else p["prompt"]
    mean_output = output_tokens if output_tokens is not None else p["output"]
    cv = p["cv"]
    rng = random.Random(seed)
    arrivals = _arrivals(rng, n, rate, pattern)
    specs = []
    for i in range(n):
        specs.append(RequestSpec(
            request_id=f"req-{i:05d}",
            prompt_tokens=_lognormal_int(rng, mean_prompt, cv),
            max_output_tokens=_lognormal_int(rng, mean_output, cv),
            arrival_time=arrivals[i],
        ))
    return specs
