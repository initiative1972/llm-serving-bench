"""Latency / throughput metrics from per-request records. Pure functions.

A "record" is a plain dict with keys: prompt_tokens, output_tokens, ttft, tpot,
latency, success. Keeping the maths dict-based (not tied to a client) is what makes
it trivially unit-testable and serialisable.
"""
from __future__ import annotations


def percentile(values, p):
    """Linear-interpolation percentile (``p`` in [0, 100]); None if empty."""
    xs = sorted(v for v in values if v is not None)
    if not xs:
        return None
    if len(xs) == 1:
        return xs[0]
    k = (len(xs) - 1) * (p / 100.0)
    lo = int(k)
    hi = min(lo + 1, len(xs) - 1)
    frac = k - lo
    return xs[lo] + (xs[hi] - xs[lo]) * frac


def _stats(values, scale=1.0):
    vs = [v for v in values if v is not None]
    if not vs:
        return {"count": 0, "mean": None, "p50": None, "p90": None,
                "p95": None, "p99": None}
    return {
        "count": len(vs),
        "mean": (sum(vs) / len(vs)) * scale,
        "p50": percentile(vs, 50) * scale,
        "p90": percentile(vs, 90) * scale,
        "p95": percentile(vs, 95) * scale,
        "p99": percentile(vs, 99) * scale,
    }


def aggregate(records, wall_time):
    """Aggregate request records into a metrics dict (latency in ms, rates per sec)."""
    ok = [r for r in records if r.get("success", True)]
    n = len(records)
    n_ok = len(ok)
    out_tokens = sum(r["output_tokens"] for r in ok)
    prompt_tokens = sum(r["prompt_tokens"] for r in ok)
    total_tokens = out_tokens + prompt_tokens
    wall = wall_time if wall_time and wall_time > 0 else None
    return {
        "requests": n,
        "successful": n_ok,
        "success_rate": (n_ok / n) if n else 0.0,
        "wall_time_s": wall_time,
        "throughput_rps": (n_ok / wall) if wall else None,
        "output_tokens_per_s": (out_tokens / wall) if wall else None,
        "total_tokens_per_s": (total_tokens / wall) if wall else None,
        "output_tokens": out_tokens,
        "prompt_tokens": prompt_tokens,
        "ttft_ms": _stats([r.get("ttft") for r in ok], scale=1000.0),
        "tpot_ms": _stats([r.get("tpot") for r in ok], scale=1000.0),
        "e2e_ms": _stats([r.get("latency") for r in ok], scale=1000.0),
    }
