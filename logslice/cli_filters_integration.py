"""CLI integration helpers for log entry filtering."""

import argparse
from datetime import datetime
from typing import Optional

from logslice.filters import (
    build_filter_chain,
    filter_by_status,
    filter_by_status_range,
    filter_by_method,
    filter_by_ip,
    filter_by_path_prefix,
    filter_by_date_range,
)


def add_filter_arguments(parser: argparse.ArgumentParser) -> None:
    """Register filter-related CLI arguments onto an ArgumentParser."""
    grp = parser.add_argument_group("filtering")
    grp.add_argument(
        "--status",
        type=int,
        metavar="CODE",
        help="Keep only entries with this exact HTTP status code.",
    )
    grp.add_argument(
        "--status-range",
        nargs=2,
        type=int,
        metavar=("MIN", "MAX"),
        help="Keep entries whose status code falls within [MIN, MAX].",
    )
    grp.add_argument(
        "--method",
        metavar="METHOD",
        help="Keep only entries with this HTTP method (e.g. GET, POST).",
    )
    grp.add_argument(
        "--ip",
        metavar="ADDRESS",
        help="Keep only entries from this client IP address.",
    )
    grp.add_argument(
        "--path-prefix",
        metavar="PREFIX",
        help="Keep only entries whose path starts with PREFIX.",
    )
    grp.add_argument(
        "--since",
        metavar="DATETIME",
        help="Keep entries at or after this ISO-8601 datetime (e.g. 2024-01-15T00:00:00).",
    )
    grp.add_argument(
        "--until",
        metavar="DATETIME",
        help="Keep entries at or before this ISO-8601 datetime.",
    )


def _parse_dt(value: Optional[str], flag: str) -> Optional[datetime]:
    if value is None:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid datetime for {flag}: '{value}'. Expected ISO-8601 format."
        )


def apply_filters_from_args(entries: list, args: argparse.Namespace) -> list:
    """Build and apply a filter chain based on parsed CLI arguments.

    Args:
        entries: List of parsed log entry dicts.
        args: Parsed argument namespace from ArgumentParser.

    Returns:
        Filtered list of entries.
    """
    filters = []

    if getattr(args, "status", None) is not None:
        filters.append(lambda e, s=args.status: filter_by_status(e, s))

    if getattr(args, "status_range", None):
        lo, hi = args.status_range
        filters.append(lambda e, lo=lo, hi=hi: filter_by_status_range(e, lo, hi))

    if getattr(args, "method", None):
        filters.append(lambda e, m=args.method: filter_by_method(e, m))

    if getattr(args, "ip", None):
        filters.append(lambda e, ip=args.ip: filter_by_ip(e, ip))

    if getattr(args, "path_prefix", None):
        filters.append(lambda e, p=args.path_prefix: filter_by_path_prefix(e, p))

    since = _parse_dt(getattr(args, "since", None), "--since")
    until = _parse_dt(getattr(args, "until", None), "--until")
    if since or until:
        filters.append(
            lambda e, s=since, u=until: filter_by_date_range(e, start=s, end=u)
        )

    return build_filter_chain(filters)(entries)
