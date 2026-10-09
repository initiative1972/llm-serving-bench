"""Client abstractions and the core per-request result record."""
from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass
class RequestResult:
    request_id: str
    prompt_tokens: int
    output_tokens: int
    start_time: float          # seconds since benchmark start (scheduled start)
    end_time: float            # seconds since benchmark start (completion)
    ttft: float | None = None  # time to first token, seconds
    success: bool = True
    error: str = ""

    @property
    def latency(self):
        """End-to-end latency (seconds)."""
        return self.end_time - self.start_time

    @property
    def tpot(self):
        """Time per output token during decode, excluding prefill/TTFT (seconds)."""
        if self.ttft is None or self.output_tokens <= 1:
            return None
        decode = self.latency - self.ttft
        return decode / (self.output_tokens - 1)

    def to_record(self):
        d = asdict(self)
        d["latency"] = self.latency
        d["tpot"] = self.tpot
        return d
