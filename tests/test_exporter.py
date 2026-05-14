"""Tests for logslice.exporter."""

import json

import pytest

from logslice.exporter import (
    available_export_formats,
    export,
    export_csv,
    export_json,
    export_ndjson,
)


SAMPLE_REPORT = {"total_requests": 3, "error_rate": 0.33}
SAMPLE_RECORDS = [
    {"ip": "1.2.3.4", "status": 200, "path": "/"},
    {"ip": "5.6.7.8", "status": 404, "path": "/missing"},
]


# ---------------------------------------------------------------------------
# export_json
# ---------------------------------------------------------------------------

def test_export_json_is_valid_json():
    result = export_json(SAMPLE_REPORT)
    parsed = json.loads(result)
    assert parsed["total_requests"] == 3


def test_export_json_indent():
    result = export_json(SAMPLE_REPORT, indent=4)
    assert "    " in result  # 4-space indent present


# ---------------------------------------------------------------------------
# export_ndjson
# ---------------------------------------------------------------------------

def test_export_ndjson_line_count():
    result = export_ndjson(SAMPLE_RECORDS)
    lines = result.strip().splitlines()
    assert len(lines) == len(SAMPLE_RECORDS)


def test_export_ndjson_each_line_valid_json():
    result = export_ndjson(SAMPLE_RECORDS)
    for line in result.strip().splitlines():
        obj = json.loads(line)
        assert "ip" in obj


def test_export_ndjson_empty():
    assert export_ndjson([]) == ""


# ---------------------------------------------------------------------------
# export_csv
# ---------------------------------------------------------------------------

def test_export_csv_has_header():
    result = export_csv(SAMPLE_RECORDS)
    first_line = result.splitlines()[0]
    assert "ip" in first_line and "status" in first_line


def test_export_csv_row_count():
    result = export_csv(SAMPLE_RECORDS)
    lines = [l for l in result.splitlines() if l.strip()]
    # header + 2 data rows
    assert len(lines) == 3


def test_export_csv_empty():
    assert export_csv([]) == ""


# ---------------------------------------------------------------------------
# available_export_formats / export dispatcher
# ---------------------------------------------------------------------------

def test_available_export_formats_contains_builtins():
    fmts = available_export_formats()
    assert "json" in fmts
    assert "ndjson" in fmts
    assert "csv" in fmts


def test_export_dispatcher_json():
    result = export(SAMPLE_REPORT, "json")
    assert json.loads(result)["total_requests"] == 3


def test_export_dispatcher_ndjson():
    result = export(SAMPLE_RECORDS, "ndjson")
    assert len(result.strip().splitlines()) == 2


def test_export_dispatcher_csv():
    result = export(SAMPLE_RECORDS, "csv")
    assert "ip" in result.splitlines()[0]


def test_export_dispatcher_unknown_raises():
    with pytest.raises(ValueError, match="Unknown export format"):
        export({}, "xml")
