"""Tests for the Apache Combined Log Format parser."""

import pytest
from logslice.parsers.apache import parse_line, parse_file
import tempfile
import os

VALID_LINE = (
    '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] '
    '"GET /apache_pb.gif HTTP/1.0" 200 2326 '
    '"http://www.example.com/start.html" '
    '"Mozilla/4.08 [en] (Win98; I)"'
)

NO_REFERER_LINE = (
    '192.168.1.10 - - [15/Jan/2024:08:30:00 +0000] '
    '"POST /api/data HTTP/1.1" 201 512 "-" "curl/7.68.0"'
)


def test_parse_line_valid():
    result = parse_line(VALID_LINE)
    assert result is not None
    assert result["remote_addr"] == "127.0.0.1"
    assert result["auth_user"] == "frank"
    assert result["status"] == 200
    assert result["body_bytes_sent"] == 2326
    assert result["method"] == "GET"
    assert result["path"] == "/apache_pb.gif"
    assert result["protocol"] == "HTTP/1.0"
    assert result["http_referer"] == "http://www.example.com/start.html"
    assert result["http_user_agent"] == "Mozilla/4.08 [en] (Win98; I)"


def test_parse_line_no_referer():
    result = parse_line(NO_REFERER_LINE)
    assert result is not None
    assert result["http_referer"] is None
    assert result["ident"] is None
    assert result["auth_user"] is None
    assert result["method"] == "POST"
    assert result["status"] == 201


def test_parse_line_empty():
    assert parse_line("") is None
    assert parse_line("   ") is None


def test_parse_line_invalid():
    assert parse_line("not a valid log line") is None
    assert parse_line("127.0.0.1 - - [bad date] \"GET / HTTP/1.1\" 200 0") is None


def test_parse_line_timestamp_format():
    result = parse_line(VALID_LINE)
    assert result is not None
    # Should be an ISO format string
    assert "2000-10-10" in result["time_local"]


def test_parse_line_zero_bytes():
    line = (
        '10.0.0.1 - - [01/Jun/2023:12:00:00 +0000] '
        '"HEAD /ping HTTP/1.1" 204 - "-" "healthcheck/1.0"'
    )
    result = parse_line(line)
    assert result is not None
    assert result["body_bytes_sent"] == 0
    assert result["status"] == 204


def test_parse_file(tmp_path):
    log_file = tmp_path / "access.log"
    log_file.write_text(
        VALID_LINE + "\n" + NO_REFERER_LINE + "\n" + "garbage line\n",
        encoding="utf-8",
    )
    results = list(parse_file(str(log_file)))
    assert len(results) == 2
    assert results[0]["remote_addr"] == "127.0.0.1"
    assert results[1]["remote_addr"] == "192.168.1.10"
