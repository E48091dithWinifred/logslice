"""Log entry filtering utilities for logslice."""

from datetime import datetime
from typing import Callable, Optional


def filter_by_status(entries: list, status_code: int) -> list:
    """Filter log entries by exact HTTP status code."""
    return [e for e in entries if e.get("status") == status_code]


def filter_by_status_range(entries: list, start: int, end: int) -> list:
    """Filter log entries by HTTP status code range (inclusive)."""
    return [e for e in entries if start <= (e.get("status") or 0) <= end]


def filter_by_method(entries: list, method: str) -> list:
    """Filter log entries by HTTP method (case-insensitive)."""
    method = method.upper()
    return [e for e in entries if (e.get("method") or "").upper() == method]


def filter_by_ip(entries: list, ip: str) -> list:
    """Filter log entries by client IP address."""
    return [e for e in entries if e.get("ip") == ip]


def filter_by_path_prefix(entries: list, prefix: str) -> list:
    """Filter log entries where the request path starts with the given prefix."""
    return [e for e in entries if (e.get("path") or "").startswith(prefix)]


def filter_by_date_range(
    entries: list,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
) -> list:
    """Filter log entries by timestamp range.

    Args:
        entries: List of parsed log entry dicts.
        start: Inclusive start datetime (UTC). None means no lower bound.
        end: Inclusive end datetime (UTC). None means no upper bound.

    Returns:
        Filtered list of entries.
    """
    result = []
    for entry in entries:
        ts = entry.get("timestamp")
        if ts is None:
            continue
        if isinstance(ts, str):
            try:
                ts = datetime.fromisoformat(ts)
            except ValueError:
                continue
        if start and ts < start:
            continue
        if end and ts > end:
            continue
        result.append(entry)
    return result


def build_filter_chain(filters: list) -> Callable[[list], list]:
    """Compose multiple filter functions into a single callable.

    Args:
        filters: List of callables that each accept and return a list of entries.

    Returns:
        A single callable that applies all filters in order.
    """
    def apply(entries: list) -> list:
        for f in filters:
            entries = f(entries)
        return entries
    return apply
