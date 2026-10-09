"""Deterministic in-process simulation 'engine'.

Models prefill + decode service time from fixed token-throughput numbers so the
whole harness (workload -> results -> metrics -> SLO -> report) runs on CPU in CI
with no GPU and no server. This is explicitly a SIMULATION, not a measurement — it
exists to test the plumbing and to let anyone generate a sample report offline.
"""
from __future__ import annotations

from dataclasses import dataclass

from .base import RequestResult


@dataclass
class MockEngine:
    name: str = "sim-engine"
    prefill_tps: float = 8000.0    # prompt tokens/second (prefill phase)
    decode_tps: float = 120.0      # output tokens/second per request (decode phase)
    base_overhead_s: float = 0.03  # fixed per-request overhead (queue + network)

    def service(self, spec):
        """Return a RequestResult carrying intrinsic service times (start=0)."""
        ttft = self.base_overhead_s + spec.prompt_tokens / self.prefill_tps
        out = max(1, spec.max_output_tokens)
        decode = (out - 1) / self.decode_tps if out > 1 else 0.0
        latency = ttft + decode
        return RequestResult(
            request_id=spec.request_id,
            prompt_tokens=spec.prompt_tokens,
            output_tokens=out,
            start_time=0.0,
            end_time=latency,
            ttft=ttft,
        )
