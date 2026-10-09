"""Cost model for self-hosted LLM serving.

Turns a throughput number into unit economics (A$/1M output tokens, A$/1k requests)
given a GPU hourly price. Prices below are ILLUSTRATIVE public list prices — not a
quote. Override ``usd_per_hr`` with your provider's real number.
"""
from __future__ import annotations

from dataclasses import dataclass

# Illustrative on-demand GPU prices (USD/hour). Update per provider / region.
GPU_PRICES_USD_HR = {
    "L4": 0.80,
    "A10G": 1.01,
    "A100-40GB": 2.40,
    "A100-80GB": 3.20,
    "H100-80GB": 4.80,
}

DEFAULT_USD_AUD = 1.52  # illustrative FX rate


@dataclass
class CostModel:
    gpu: str = "A100-80GB"
    gpu_count: int = 1
    usd_per_hr: float | None = None
    usd_aud: float = DEFAULT_USD_AUD

    def hourly_usd(self):
        price = self.usd_per_hr
        if price is None:
            if self.gpu not in GPU_PRICES_USD_HR:
                raise KeyError(f"no price for GPU '{self.gpu}'; pass usd_per_hr")
            price = GPU_PRICES_USD_HR[self.gpu]
        return price * self.gpu_count

    def hourly_aud(self):
        return self.hourly_usd() * self.usd_aud

    def aud_per_1m_output_tokens(self, output_tokens_per_s):
        if not output_tokens_per_s or output_tokens_per_s <= 0:
            return None
        per_s = self.hourly_aud() / 3600.0
        return per_s / output_tokens_per_s * 1_000_000

    def aud_per_1k_requests(self, throughput_rps):
        if not throughput_rps or throughput_rps <= 0:
            return None
        per_s = self.hourly_aud() / 3600.0
        return per_s / throughput_rps * 1000
