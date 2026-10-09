"""Comparison report + regression gate across benchmark runs. Pure functions."""
from __future__ import annotations

import json
from pathlib import Path


def _fmt(v, nd=1):
    return "—" if v is None else f"{v:,.{nd}f}"


def comparison_table(runs):
    """``runs``: list of {name, metrics, aud_per_1m, slo_passed}."""
    header = ("| Config | TTFT p90 (ms) | TPOT p90 (ms) | E2E p99 (ms) "
              "| Throughput (req/s) | Out tok/s | A$/1M tok | SLO |")
    sep = "|" + "---|" * 8
    rows = [header, sep]
    for r in runs:
        met = r["metrics"]
        rows.append(
            f"| {r['name']} | {_fmt(met['ttft_ms']['p90'])} "
            f"| {_fmt(met['tpot_ms']['p90'])} | {_fmt(met['e2e_ms']['p99'])} "
            f"| {_fmt(met['throughput_rps'], 2)} "
            f"| {_fmt(met['output_tokens_per_s'])} "
            f"| {_fmt(r.get('aud_per_1m'), 2)} "
            f"| {'PASS' if r.get('slo_passed') else 'FAIL'} |"
        )
    return "\n".join(rows)


def detect_regressions(baseline, candidate, tol=0.10):
    """Flag latency / cost up or throughput down beyond ``tol`` fraction."""
    issues = []

    def up(metric, b, c):
        if b is None or c is None or b <= 0:
            return
        if (c - b) / b > tol:
            issues.append(f"{metric} up {(c - b) / b * 100:.0f}% "
                          f"({b:.1f} -> {c:.1f})")

    def down(metric, b, c):
        if b is None or c is None or b <= 0:
            return
        if (b - c) / b > tol:
            issues.append(f"{metric} down {(b - c) / b * 100:.0f}% "
                          f"({b:.1f} -> {c:.1f})")

    up("ttft_p90_ms", baseline["ttft_ms"]["p90"], candidate["ttft_ms"]["p90"])
    up("e2e_p99_ms", baseline["e2e_ms"]["p99"], candidate["e2e_ms"]["p99"])
    down("throughput_rps", baseline["throughput_rps"],
         candidate["throughput_rps"])
    return issues


def to_markdown(runs, title="LLM serving benchmark"):
    lines = [f"# {title}", "", comparison_table(runs), ""]
    return "\n".join(lines)


def write_report(runs, path, title="LLM serving benchmark"):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(to_markdown(runs, title), encoding="utf-8")
    return str(p)


def write_json(obj, path):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, default=str), encoding="utf-8")
    return str(p)
