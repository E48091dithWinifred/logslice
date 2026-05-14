"""Export parsed log summaries to various file formats (JSON, CSV, NDJSON)."""

import csv
import io
import json
from typing import Any, Dict, List


def export_json(report: Dict[str, Any], indent: int = 2) -> str:
    """Serialize report to a pretty-printed JSON string."""
    return json.dumps(report, indent=indent, default=str)


def export_ndjson(records: List[Dict[str, Any]]) -> str:
    """Serialize a list of records to newline-delimited JSON."""
    lines = [json.dumps(record, default=str) for record in records]
    return "\n".join(lines)


def export_csv(records: List[Dict[str, Any]]) -> str:
    """Serialize a list of flat records to CSV format.

    All records are expected to share the same keys. If the list is empty,
    an empty string is returned.
    """
    if not records:
        return ""

    output = io.StringIO()
    fieldnames = list(records[0].keys())
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
        lineterminator="\n",
    )
    writer.writeheader()
    writer.writerows(records)
    return output.getvalue()


_EXPORTERS = {
    "json": export_json,
    "ndjson": export_ndjson,
    "csv": export_csv,
}


def available_export_formats() -> List[str]:
    """Return the list of supported export format names."""
    return list(_EXPORTERS.keys())


def export(data: Any, fmt: str) -> str:
    """Export *data* using the named format.

    Args:
        data: A dict (for json) or list of dicts (for ndjson / csv).
        fmt:  One of 'json', 'ndjson', 'csv'.

    Raises:
        ValueError: If *fmt* is not a known export format.
    """
    if fmt not in _EXPORTERS:
        raise ValueError(
            f"Unknown export format '{fmt}'. "
            f"Available: {', '.join(available_export_formats())}"
        )
    return _EXPORTERS[fmt](data)
