#!/usr/bin/env python3
"""
Command-line interface for logslice.

Provides a CLI entry point for parsing log files and outputting
structured JSON summaries.

Usage:
    logslice [OPTIONS] <logfile>

Examples:
    logslice access.log
    logslice --format nginx --output summary.json access.log
    logslice --pretty access.log
"""

import argparse
import json
import sys
from pathlib import Path

from logslice.parsers import nginx
from logslice.aggregator import summarize


SUPPORTED_FORMATS = {
    "nginx": nginx,
}


def build_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="logslice",
        description="A fast log file parser and aggregator that outputs structured JSON summaries.",
    )

    parser.add_argument(
        "logfile",
        type=str,
        help="Path to the log file to parse.",
    )

    parser.add_argument(
        "--format",
        "-f",
        type=str,
        default="nginx",
        choices=SUPPORTED_FORMATS.keys(),
        help="Log format to use for parsing (default: nginx).",
    )

    parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Path to write JSON output. If not specified, prints to stdout.",
    )

    parser.add_argument(
        "--pretty",
        "-p",
        action="store_true",
        default=False,
        help="Pretty-print the JSON output with indentation.",
    )

    parser.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        default=False,
        help="Suppress warnings and informational messages.",
    )

    return parser


def run(args=None) -> int:
    """
    Main entry point for the CLI.

    Args:
        args: Optional list of CLI arguments (defaults to sys.argv).

    Returns:
        Exit code (0 for success, non-zero for failure).
    """
    parser = build_parser()
    parsed = parser.parse_args(args)

    log_path = Path(parsed.logfile)

    if not log_path.exists():
        print(f"Error: File not found: {log_path}", file=sys.stderr)
        return 1

    if not log_path.is_file():
        print(f"Error: Not a file: {log_path}", file=sys.stderr)
        return 1

    # Select the appropriate parser module
    format_module = SUPPORTED_FORMATS.get(parsed.format)
    if format_module is None:
        print(f"Error: Unsupported format '{parsed.format}'", file=sys.stderr)
        return 1

    if not parsed.quiet:
        print(f"Parsing {log_path} as {parsed.format} format...", file=sys.stderr)

    # Parse the log file and aggregate results
    entries = format_module.parse_file(str(log_path))
    summary = summarize(entries)

    # Serialize to JSON
    indent = 2 if parsed.pretty else None
    output_json = json.dumps(summary, indent=indent, default=str)

    # Write output
    if parsed.output:
        output_path = Path(parsed.output)
        try:
            output_path.write_text(output_json, encoding="utf-8")
            if not parsed.quiet:
                print(f"Summary written to {output_path}", file=sys.stderr)
        except OSError as e:
            print(f"Error writing output file: {e}", file=sys.stderr)
            return 1
    else:
        print(output_json)

    return 0


if __name__ == "__main__":
    sys.exit(run())
