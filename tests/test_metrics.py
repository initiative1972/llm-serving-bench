from src.metrics import aggregate, percentile


def test_percentile_basic():
    assert percentile([1, 2, 3, 4], 50) == 2.5
    assert percentile([10], 99) == 10
    assert percentile([], 50) is None


def test_aggregate_throughput():
    records = [
        {"prompt_tokens": 10, "output_tokens": 20, "ttft": 0.1,
         "tpot": 0.01, "latency": 0.3, "success": True},
        {"prompt_tokens": 10, "output_tokens": 20, "ttft": 0.2,
         "tpot": 0.02, "latency": 0.5, "success": True},
    ]
    met = aggregate(records, wall_time=1.0)
    assert met["requests"] == 2
    assert met["successful"] == 2
    assert met["throughput_rps"] == 2.0
    assert met["output_tokens"] == 40
    assert met["output_tokens_per_s"] == 40.0
    assert met["ttft_ms"]["p50"] is not None


def test_aggregate_handles_failures():
    records = [
        {"prompt_tokens": 10, "output_tokens": 20, "ttft": 0.1,
         "tpot": 0.01, "latency": 0.3, "success": True},
        {"prompt_tokens": 10, "output_tokens": 0, "ttft": None,
         "tpot": None, "latency": 0.0, "success": False},
    ]
    met = aggregate(records, wall_time=2.0)
    assert met["requests"] == 2
    assert met["successful"] == 1
    assert met["success_rate"] == 0.5


def test_zero_wall_time_safe():
    records = [{"prompt_tokens": 1, "output_tokens": 1, "ttft": 0.1,
                "tpot": None, "latency": 0.1, "success": True}]
    met = aggregate(records, wall_time=0)
    assert met["throughput_rps"] is None
