"""CLI helpers for the --export-format / --output-file flags."""

import argparse
import sys
from typing import Any, Dict, List, Optional

from logslice.exporter import available_export_formats, export


def add_export_arguments(parser: argparse.ArgumentParser) -> None:
    """Attach export-related arguments to *parser*."""
    parser.add_argument(
        "--export-format",
        dest="export_format",
        choices=available_export_formats(),
        default="json",
        metavar="FORMAT",
        help=(
            "Output format for the exported data. "
            f"Choices: {', '.join(available_export_formats())} (default: json)"
        ),
    )
    parser.add_argument(
        "--output-file",
        dest="output_file",
        default=None,
        metavar="PATH",
        help="Write output to PATH instead of stdout.",
    )


def write_export(
    data: Any,
    fmt: str,
    output_file: Optional[str] = None,
) -> None:
    """Serialize *data* with *fmt* and write to *output_file* or stdout.

    Args:
        data:        The payload to export (dict or list of dicts).
        fmt:         Export format name ('json', 'ndjson', 'csv').
        output_file: Destination file path; ``None`` means stdout.
    """
    serialized = export(data, fmt)

    if output_file:
        with open(output_file, "w", encoding="utf-8") as fh:
            fh.write(serialized)
            if not serialized.endswith("\n"):
                fh.write("\n")
    else:
        sys.stdout.write(serialized)
        if not serialized.endswith("\n"):
            sys.stdout.write("\n")
