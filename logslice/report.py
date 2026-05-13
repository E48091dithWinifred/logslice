"""High-level report builder that combines aggregation with stats."""

from collections import Counter
from typing import Any

from logslice.stats import top_n, response_time_stats, error_rate


def build_report(
    records: list[dict[str, Any]],
    top: int = 10,
) -> dict[str, Any]:
    """Build a structured report from a list of parsed log records.

    Args:
        records: Parsed log entries (dicts with at least 'status', 'method',
                 'path', 'ip', and optionally 'response_time').
        top: How many top entries to include in ranked lists.

    Returns:
        A dict suitable for JSON serialisation.
    """
    if not records:
        return {
            "total_requests": 0,
            "error_rate": 0.0,
            "status_counts": {},
            "top_ips": [],
            "top_paths": [],
            "top_methods": [],
            "response_time_stats": response_time_stats([]),
        }

    status_counter: Counter = Counter()
    ip_counter: Counter = Counter()
    path_counter: Counter = Counter()
    method_counter: Counter = Counter()
    times: list[float] = []

    for rec in records:
        if rec.get("status"):
            status_counter[str(rec["status"])] += 1
        if rec.get("ip"):
            ip_counter[rec["ip"]] += 1
        if rec.get("path"):
            path_counter[rec["path"]] += 1
        if rec.get("method"):
            method_counter[rec["method"]] += 1
        rt = rec.get("response_time")
        if rt is not None:
            try:
                times.append(float(rt))
            except (TypeError, ValueError):
                pass

    return {
        "total_requests": len(records),
        "error_rate": error_rate(dict(status_counter)),
        "status_counts": dict(status_counter),
        "top_ips": top_n(ip_counter, top),
        "top_paths": top_n(path_counter, top),
        "top_methods": top_n(method_counter, top),
        "response_time_stats": response_time_stats(times),
    }
