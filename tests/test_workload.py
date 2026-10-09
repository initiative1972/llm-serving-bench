import pytest

from src.workload import PROFILES, generate_requests


def test_count_and_determinism():
    a = generate_requests(50, profile="chat", seed=7)
    b = generate_requests(50, profile="chat", seed=7)
    assert len(a) == 50
    assert [x.prompt_tokens for x in a] == [x.prompt_tokens for x in b]


def test_positive_tokens():
    specs = generate_requests(100, profile="rag", seed=1)
    assert all(s.prompt_tokens >= 1 and s.max_output_tokens >= 1 for s in specs)


def test_poisson_arrivals_monotonic():
    specs = generate_requests(100, profile="chat", rate=10, pattern="poisson",
                              seed=3)
    arr = [s.arrival_time for s in specs]
    assert arr == sorted(arr)
    assert arr[0] >= 0


def test_offline_zero_arrivals():
    specs = generate_requests(10, pattern="offline")
    assert all(s.arrival_time == 0.0 for s in specs)


def test_overrides_apply():
    specs = generate_requests(5, profile="chat", prompt_tokens=10,
                              output_tokens=10, seed=1)
    assert len(specs) == 5


def test_unknown_profile_raises():
    with pytest.raises(ValueError):
        generate_requests(5, profile="nope")


def test_profiles_present():
    assert "chat" in PROFILES and "rag" in PROFILES
