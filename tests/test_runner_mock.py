import pytest

from src.clients.mock import MockEngine
from src.runner import simulate, summarise
from src.slo import SLO, evaluate
from src.workload import generate_requests


def test_simulation_end_to_end():
    specs = generate_requests(100, profile="chat", seed=5)
    run = simulate(MockEngine(), specs, concurrency=8)
    assert run.wall_time > 0
    assert len(run.results) == 100
    met = summarise(run)
    assert met["requests"] == 100
    assert met["throughput_rps"] > 0
    assert met["ttft_ms"]["p50"] is not None


def test_higher_concurrency_not_slower():
    specs = generate_requests(80, profile="chat", pattern="offline", seed=9)
    w1 = simulate(MockEngine(), specs, concurrency=1).wall_time
    w8 = simulate(MockEngine(), specs, concurrency=8).wall_time
    assert w8 <= w1


def test_concurrency_validation():
    specs = generate_requests(5)
    with pytest.raises(ValueError):
        simulate(MockEngine(), specs, concurrency=0)


def test_slo_eval_on_sim():
    specs = generate_requests(50, seed=2)
    run = simulate(MockEngine(), specs, concurrency=4)
    met = summarise(run)
    slo = SLO(ttft_p90_ms=5000, e2e_p99_ms=60000, min_success_rate=0.99)
    ev = evaluate(met, slo)
    assert ev["passed"] is True
