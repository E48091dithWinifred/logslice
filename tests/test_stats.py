"""Tests for logslice.stats."""

from collections import Counter

import pytest

from logslice.stats import top_n, compute_percentile, response_time_stats, error_rate


def test_top_n_basic():
    c = Counter({"a": 10, "b": 3, "c": 7})
    result = top_n(c, 2)
    assert result == [{"value": "a", "count": 10}, {"value": "c", "count": 7}]


def test_top_n_empty():
    assert top_n(Counter(), 5) == []


def test_compute_percentile_median():
    values = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert compute_percentile(values, 50) == 3.0


def test_compute_percentile_min_max():
    values = [1.0, 2.0, 3.0]
    assert compute_percentile(values, 0) == 1.0
    assert compute_percentile(values, 100) == 3.0


def test_compute_percentile_empty():
    assert compute_percentile([], 50) == 0.0


def test_response_time_stats_basic():
    times = [0.1, 0.2, 0.3, 0.4, 0.5]
    stats = response_time_stats(times)
    assert stats["min"] == 0.1
    assert stats["max"] == 0.5
    assert stats["mean"] == pytest.approx(0.3, abs=1e-4)
    assert "p50" in stats
    assert "p90" in stats
    assert "p99" in stats


def test_response_time_stats_empty():
    stats = response_time_stats([])
    assert all(v == 0.0 for v in stats.values())


def test_error_rate_no_errors():
    counts = {"200": 50, "301": 10}
    assert error_rate(counts) == 0.0


def test_error_rate_mixed():
    counts = {"200": 80, "404": 10, "500": 10}
    assert error_rate(counts) == pytest.approx(0.2, abs=1e-4)


def test_error_rate_empty():
    assert error_rate({}) == 0.0
