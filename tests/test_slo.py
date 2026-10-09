from src.slo import SLO, evaluate


def _metrics(ttft_p90, e2e_p99, rps, success=1.0):
    return {
        "ttft_ms": {"p90": ttft_p90},
        "e2e_ms": {"p99": e2e_p99},
        "throughput_rps": rps,
        "success_rate": success,
    }


def test_all_pass():
    slo = SLO(ttft_p90_ms=500, e2e_p99_ms=8000, min_throughput_rps=1.0)
    ev = evaluate(_metrics(200, 4000, 5.0), slo, aud_per_1m_tokens=1.0)
    assert ev["passed"] is True


def test_ttft_breach():
    slo = SLO(ttft_p90_ms=100)
    ev = evaluate(_metrics(200, 4000, 5.0), slo)
    assert ev["passed"] is False


def test_cost_breach():
    slo = SLO(max_aud_per_1m_tokens=0.5)
    ev = evaluate(_metrics(200, 4000, 5.0), slo, aud_per_1m_tokens=1.0)
    assert ev["passed"] is False


def test_headroom_present():
    slo = SLO(ttft_p90_ms=400)
    ev = evaluate(_metrics(200, 4000, 5.0), slo)
    ttft = [c for c in ev["checks"] if c["name"] == "ttft_p90_ms"][0]
    assert ttft["headroom"] == 0.5
