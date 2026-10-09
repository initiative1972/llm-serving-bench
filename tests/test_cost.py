import pytest

from src.cost import CostModel


def test_hourly_from_table():
    cm = CostModel(gpu="A100-80GB", gpu_count=1, usd_aud=1.5)
    assert cm.hourly_usd() == 3.20
    assert abs(cm.hourly_aud() - 4.80) < 1e-9


def test_aud_per_1m_tokens():
    cm = CostModel(gpu="A100-80GB", usd_aud=1.5)  # 4.80 AUD/hr
    val = cm.aud_per_1m_output_tokens(100.0)
    expected = (4.80 / 3600.0) / 100.0 * 1_000_000
    assert abs(val - expected) < 1e-6


def test_zero_throughput_none():
    cm = CostModel()
    assert cm.aud_per_1m_output_tokens(0) is None
    assert cm.aud_per_1k_requests(0) is None


def test_custom_price_and_count():
    cm = CostModel(gpu="whatever", usd_per_hr=2.0, gpu_count=2, usd_aud=1.0)
    assert cm.hourly_usd() == 4.0


def test_unknown_gpu_raises():
    cm = CostModel(gpu="does-not-exist")
    with pytest.raises(KeyError):
        cm.hourly_usd()
