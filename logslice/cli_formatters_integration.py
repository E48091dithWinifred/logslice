"""Integration helpers: wire formatters into the CLI output pipeline."""

from typing import Any, Dict, Optional, TextIO
import sys

from logslice.formatters import format_output, available_formatters


def write_summary(
    summary: Dict[str, Any],
    fmt: str = "json",
    output: Optional[TextIO] = None,
) -> None:
    """Format *summary* and write it to *output* (default: stdout).

    Parameters
    ----------
    summary:
        Aggregated log summary produced by :func:`logslice.aggregator.summarize`.
    fmt:
        Formatter name.  Must be one of :func:`available_formatters`.
    output:
        File-like object to write to.  Defaults to ``sys.stdout``.

    Raises
    ------
    KeyError
        If *fmt* is not a registered formatter.
    """
    if output is None:
        output = sys.stdout

    rendered = format_output(summary, fmt=fmt)
    output.write(rendered)
    if not rendered.endswith("\n"):
        output.write("\n")


def add_format_argument(parser) -> None:
    """Add ``--format`` / ``-f`` argument to an :class:`argparse.ArgumentParser`.

    Intended to be called from :func:`logslice.cli.build_parser` so the CLI
    exposes all registered formatters automatically.

    Parameters
    ----------
    parser:
        An ``argparse.ArgumentParser`` (or sub-parser) instance.
    """
    choices = available_formatters()
    parser.add_argument(
        "-f",
        "--format",
        dest="output_format",
        choices=choices,
        default="json",
        metavar="FORMAT",
        help=(
            "Output format for the summary. "
            f"Available: {', '.join(choices)} (default: json)"
        ),
    )
