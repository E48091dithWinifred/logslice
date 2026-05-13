"""Tests for logslice output formatters."""

import json
import pytest
from logslice.formatters import (
    format_output,
    available_formatters,
    get_formatter,
    register_formatter,
)

SAMPLE_SUMMARY = {
    "total_requests": 42,
    "status_codes": {"200": 35, "404": 5, "500": 2},
    "top_ips": ["192.168.1.1", "10.0.0.2"],
    "format": "nginx",
}


def test_available_formatters_includes_builtins():
    fmts = available_formatters()
    assert "json" in fmts
    assert "csv" in fmts
    assert "text" in fmts


def test_get_formatter_known():
    fn = get_formatter("json")
    assert callable(fn)


def test_get_formatter_unknown_raises():
    with pytest.raises(KeyError, match="Unknown formatter"):
        get_formatter("xml")


def test_format_json_valid():
    output = format_output(SAMPLE_SUMMARY, fmt="json")
    parsed = json.loads(output)
    assert parsed["total_requests"] == 42
    assert parsed["status_codes"]["200"] == 35


def test_format_json_default():
    output = format_output(SAMPLE_SUMMARY)
    parsed = json.loads(output)
    assert "total_requests" in parsed


def test_format_csv_contains_headers():
    output = format_output(SAMPLE_SUMMARY, fmt="csv")
    lines = output.strip().splitlines()
    assert len(lines) == 2
    assert "total_requests" in lines[0]
    assert "status_codes.200" in lines[0]


def test_format_csv_values():
    output = format_output(SAMPLE_SUMMARY, fmt="csv")
    lines = output.strip().splitlines()
    assert "42" in lines[1]


def test_format_text_contains_keys():
    output = format_output(SAMPLE_SUMMARY, fmt="text")
    assert "total_requests: 42" in output
    assert "status_codes:" in output
    assert "  200: 35" in output


def test_format_text_list_joined():
    output = format_output(SAMPLE_SUMMARY, fmt="text")
    assert "192.168.1.1" in output


def test_register_custom_formatter():
    @register_formatter("upper")
    def _upper(summary):
        return str(summary).upper()

    assert "upper" in available_formatters()
    result = format_output({"key": "val"}, fmt="upper")
    assert "KEY" in result
