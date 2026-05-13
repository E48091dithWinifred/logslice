"""Output formatters for logslice summaries."""

import json
import csv
import io
from typing import Any, Dict

_FORMATTERS = {}


def register_formatter(name: str):
    """Decorator to register an output formatter."""
    def decorator(fn):
        _FORMATTERS[name] = fn
        return fn
    return decorator


def available_formatters():
    """Return list of registered formatter names."""
    return list(_FORMATTERS.keys())


def get_formatter(name: str):
    """Retrieve a formatter by name, raising KeyError if not found."""
    if name not in _FORMATTERS:
        raise KeyError(f"Unknown formatter: '{name}'. Available: {available_formatters()}")
    return _FORMATTERS[name]


def format_output(summary: Dict[str, Any], fmt: str = "json") -> str:
    """Format a summary dict using the named formatter."""
    formatter = get_formatter(fmt)
    return formatter(summary)


@register_formatter("json")
def _format_json(summary: Dict[str, Any]) -> str:
    """Render summary as pretty-printed JSON."""
    return json.dumps(summary, indent=2, default=str)


@register_formatter("csv")
def _format_csv(summary: Dict[str, Any]) -> str:
    """Render summary top-level keys as a single-row CSV."""
    buf = io.StringIO()
    flat = {}
    for key, value in summary.items():
        if isinstance(value, dict):
            for sub_key, sub_val in value.items():
                flat[f"{key}.{sub_key}"] = sub_val
        elif isinstance(value, list):
            flat[key] = "|".join(str(v) for v in value)
        else:
            flat[key] = value
    writer = csv.DictWriter(buf, fieldnames=list(flat.keys()))
    writer.writeheader()
    writer.writerow(flat)
    return buf.getvalue().rstrip()


@register_formatter("text")
def _format_text(summary: Dict[str, Any]) -> str:
    """Render summary as human-readable plain text."""
    lines = []
    for key, value in summary.items():
        if isinstance(value, dict):
            lines.append(f"{key}:")
            for sub_key, sub_val in value.items():
                lines.append(f"  {sub_key}: {sub_val}")
        elif isinstance(value, list):
            lines.append(f"{key}: {', '.join(str(v) for v in value)}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)
