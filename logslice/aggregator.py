"""Aggregation utilities for logslice parsed log entries."""

from collections import Counter, defaultdict
from typing import Iterable


def summarize(entries: Iterable[dict]) -> dict:
    """Produce a structured JSON-serialisable summary from an iterable of
    parsed log entry dicts.

    Works with both nginx and apache parsed entries as they share common
    field names (status, method, path, remote_addr, body_bytes_sent).
    """
    total = 0
    status_counts: Counter = Counter()
    method_counts: Counter = Counter()
    path_counts: Counter = Counter()
    ip_counts: Counter = Counter()
    total_bytes = 0
    error_count = 0  # 4xx + 5xx

    for entry in entries:
        total += 1

        status = entry.get("status")
        if status is not None:
            status_counts[str(status)] += 1
            if status >= 400:
                error_count += 1

        method = entry.get("method")
        if method:
            method_counts[method] += 1

        path = entry.get("path")
        if path:
            path_counts[path] += 1

        remote_addr = entry.get("remote_addr")
        if remote_addr:
            ip_counts[remote_addr] += 1

        bytes_sent = entry.get("body_bytes_sent", 0) or 0
        total_bytes += bytes_sent

    top_paths = [p for p, _ in path_counts.most_common(10)]
    top_ips = [ip for ip, _ in ip_counts.most_common(10)]

    return {
        "total_requests": total,
        "total_bytes_sent": total_bytes,
        "error_count": error_count,
        "error_rate": round(error_count / total, 4) if total > 0 else 0.0,
        "status_counts": dict(status_counts),
        "method_counts": dict(method_counts),
        "top_paths": top_paths,
        "top_ips": top_ips,
    }
