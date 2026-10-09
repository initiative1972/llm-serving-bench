"""Quantisation format metadata + VRAM-fit estimation.

Lets you answer "will a 7B AWQ model fit on a 24 GB card with room for KV cache?"
before you ever boot a GPU. Numbers are first-order estimates, not exact.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class QuantFormat:
    name: str
    bits: float
    bytes_per_param: float
    note: str


FORMATS = {
    "fp16": QuantFormat("fp16", 16, 2.0, "Baseline half precision"),
    "bf16": QuantFormat("bf16", 16, 2.0, "Baseline; stable, Ampere+"),
    "fp8":  QuantFormat("fp8", 8, 1.0, "Hopper+; near-FP16 quality"),
    "int8": QuantFormat("int8", 8, 1.0, "LLM.int8 / W8A8"),
    "awq":  QuantFormat("awq", 4, 0.5, "4-bit weight-only; strong quality retention"),
    "gptq": QuantFormat("gptq", 4, 0.5, "4-bit PTQ; widely supported"),
    "gguf_q4_k_m": QuantFormat("gguf_q4_k_m", 4.5, 0.56,
                               "llama.cpp k-quant; CPU / edge friendly"),
}


def weight_vram_gb(params_billion, fmt):
    q = FORMATS[fmt]
    return params_billion * 1e9 * q.bytes_per_param / (1024 ** 3)


def estimate_vram_gb(params_billion, fmt, kv_cache_gb=2.0, overhead_frac=0.15):
    """Rough serving VRAM = (weights + KV cache) * (1 + framework overhead)."""
    weights = weight_vram_gb(params_billion, fmt)
    return (weights + kv_cache_gb) * (1 + overhead_frac)


def fits(params_billion, fmt, gpu_vram_gb, kv_cache_gb=2.0):
    need = estimate_vram_gb(params_billion, fmt, kv_cache_gb)
    return {
        "fmt": fmt,
        "need_gb": need,
        "gpu_vram_gb": gpu_vram_gb,
        "fits": need <= gpu_vram_gb,
        "headroom_gb": gpu_vram_gb - need,
    }
