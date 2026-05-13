"""Statistical aggregation utilities for log summaries."""

from collections import Counter
from typing import Any


def top_n(counter: Counter, n: int = 10) -> list[dict[str, Any]]:
    """Return the top N entries from a Counter as a list of dicts."""
    return [{"value": val, "count": cnt} for val, cnt in counter.most_common(n)]


def compute_percentile(sorted_values: list[float], percentile: float) -> float:
    """Compute a percentile from a sorted list of numeric values.

    Args:
        sorted_values: A sorted list of floats.
        percentile: A value between 0 and 100.

    Returns:
        The computed percentile value.
    """
    if not sorted_values:
        return 0.0
    if percentile <= 0:
        return sorted_values[0]
    if percentile >= 100:
        return sorted_values[-1]
    index = (percentile / 100) * (len(sorted_values) - 1)
    lower = int(index)
    upper = lower + 1
    if upper >= len(sorted_values):
        return float(sorted_values[lower])
    fraction = index - lower
    return sorted_values[lower] + fraction * (sorted_values[upper] - sorted_values[lower])


def response_time_stats(times: list[float]) -> dict[str, float]:
    """Compute summary statistics for a list of response times.

    Returns a dict with min, max, mean, p50, p90, p99.
    """
    if not times:
        return {"min": 0.0, "max": 0.0, "mean": 0.0, "p50": 0.0, "p90": 0.0, "p99": 0.0}
    sorted_times = sorted(times)
    total = sum(sorted_times)
    return {
        "min": round(sorted_times[0], 4),
        "max": round(sorted_times[-1], 4),
        "mean": round(total / len(sorted_times), 4),
        "p50": round(compute_percentile(sorted_times, 50), 4),
        "p90": round(compute_percentile(sorted_times, 90), 4),
        "p99": round(compute_percentile(sorted_times, 99), 4),
    }


def error_rate(status_counts: dict[str, int]) -> float:
    """Compute the fraction of requests that resulted in a 4xx or 5xx status."""
    total = sum(status_counts.values())
    if total == 0:
        return 0.0
    errors = sum(v for k, v in status_counts.items() if k.startswith(("4", "5")))
    return round(errors / total, 4)
