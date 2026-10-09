from src.report import comparison_table, detect_regressions, to_markdown


def _met(ttft, e2e, rps, outps):
    return {
        "ttft_ms": {"p90": ttft}, "tpot_ms": {"p90": 10.0},
        "e2e_ms": {"p99": e2e}, "throughput_rps": rps,
        "output_tokens_per_s": outps,
    }


def test_table_has_rows():
    runs = [{"name": "vllm-awq", "metrics": _met(120, 3000, 8.0, 900),
             "aud_per_1m": 1.2, "slo_passed": True}]
    tbl = comparison_table(runs)
    assert "vllm-awq" in tbl
    assert "PASS" in tbl


def test_regression_detects_throughput_drop():
    base = _met(100, 3000, 10.0, 1000)
    cand = _met(100, 3000, 8.0, 800)
    issues = detect_regressions(base, cand, tol=0.1)
    assert any("throughput" in i for i in issues)


def test_regression_detects_latency_rise():
    base = _met(100, 3000, 10.0, 1000)
    cand = _met(130, 3000, 10.0, 1000)
    issues = detect_regressions(base, cand, tol=0.1)
    assert any("ttft" in i for i in issues)


def test_no_regression_when_better():
    base = _met(100, 3000, 10.0, 1000)
    cand = _met(90, 2900, 11.0, 1100)
    assert detect_regressions(base, cand) == []


def test_to_markdown_title():
    runs = [{"name": "r", "metrics": _met(1, 1, 1, 1),
             "aud_per_1m": None, "slo_passed": False}]
    md = to_markdown(runs, title="Hello Bench")
    assert md.startswith("# Hello Bench")
