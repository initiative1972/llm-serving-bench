from src.quantization import (FORMATS, estimate_vram_gb, fits, weight_vram_gb)


def test_fp16_weight_vram():
    gb = weight_vram_gb(7, "fp16")  # ~13.0 GB
    assert 12.5 < gb < 13.5


def test_awq_smaller_than_fp16():
    assert weight_vram_gb(7, "awq") < weight_vram_gb(7, "fp16")


def test_fits_logic():
    assert fits(7, "awq", gpu_vram_gb=24)["fits"] is True
    assert fits(70, "fp16", gpu_vram_gb=24)["fits"] is False


def test_estimate_includes_overhead():
    assert estimate_vram_gb(7, "fp16") > weight_vram_gb(7, "fp16")


def test_all_formats_have_positive_bytes():
    assert all(f.bytes_per_param > 0 for f in FORMATS.values())
