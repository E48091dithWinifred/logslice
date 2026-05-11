"""Aggregate parsed log records into a structured JSON summary."""

from collections import Counter
from typing import Any


def summarize(records: list[dict]) -> dict[str, Any]:
    """Produce a summary dict from a list of parsed log records.

    Summary includes:
    - total request count
    - status code distribution
    - top 10 requested paths
    - top 10 remote addresses
    - total bytes transferred
    - average bytes per request
    """
    if not records:
        return {
            "total_requests": 0,
            "status_distribution": {},
            "top_paths": [],
            "top_remote_addrs": [],
            "total_bytes": 0,
            "avg_bytes_per_request": 0.0,
        }

    status_counter: Counter = Counter()
    path_counter: Counter = Counter()
    addr_counter: Counter = Counter()
    total_bytes = 0

    for record in records:
        status_counter[str(record.get("status", "unknown"))] += 1
        path = record.get("path", "")
        if path:
            path_counter[path] += 1
        addr = record.get("remote_addr", "")
        if addr:
            addr_counter[addr] += 1
        total_bytes += record.get("body_bytes_sent", 0)

    total = len(records)

    return {
        "total_requests": total,
        "status_distribution": dict(status_counter.most_common()),
        "top_paths": [
            {"path": p, "count": c} for p, c in path_counter.most_common(10)
        ],
        "top_remote_addrs": [
            {"addr": a, "count": c} for a, c in addr_counter.most_common(10)
        ],
        "total_bytes": total_bytes,
        "avg_bytes_per_request": round(total_bytes / total, 2),
    }
