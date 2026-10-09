"""Service-level objective definition + evaluation against a metrics dict.

The benchmark gates PASS / FAIL on these so a config can be accepted or rejected
objectively (and so CI can fail a regression). Each check reports headroom so you
can see how close you are to the limit, not just pass/fail.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SLO:
    ttft_p90_ms: float | None = None
    e2e_p99_ms: float | None = None
    min_throughput_rps: float | None = None
    max_aud_per_1m_tokens: float | None = None
    min_success_rate: float = 0.99


def _check(name, actual, limit, mode):
    """``mode`` 'max' => actual <= limit; 'min' => actual >= limit."""
    if limit is None:
        return None
    if actual is None:
        return {"name": name, "actual": None, "limit": limit,
                "passed": False, "headroom": None}
    if mode == "max":
        passed = actual <= limit
        headroom = (limit - actual) / limit if limit else None
    else:
        passed = actual >= limit
        headroom = (actual - limit) / limit if limit else None
    return {"name": name, "actual": actual, "limit": limit,
            "passed": passed, "headroom": headroom}


def evaluate(metrics, slo, aud_per_1m_tokens=None):
    checks = [
        _check("ttft_p90_ms", metrics["ttft_ms"]["p90"], slo.ttft_p90_ms, "max"),
        _check("e2e_p99_ms", metrics["e2e_ms"]["p99"], slo.e2e_p99_ms, "max"),
        _check("throughput_rps", metrics["throughput_rps"],
               slo.min_throughput_rps, "min"),
        _check("aud_per_1m_tokens", aud_per_1m_tokens,
               slo.max_aud_per_1m_tokens, "max"),
        _check("success_rate", metrics["success_rate"],
               slo.min_success_rate, "min"),
    ]
    checks = [c for c in checks if c is not None]
    passed = all(c["passed"] for c in checks) if checks else True
    return {"passed": passed, "checks": checks}
