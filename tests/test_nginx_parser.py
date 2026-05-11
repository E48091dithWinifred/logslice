"""Tests for the Nginx log parser and aggregator."""

import pytest
from logslice.parsers.nginx import parse_line
from logslice.aggregator import summarize

SAMPLE_LINE = (
    '127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] '
    '"GET /apache_pb.gif HTTP/1.0" 200 2326 '
    '"http://www.example.com/start.html" '
    '"Mozilla/5.0 (compatible; MSIE 6.0)"'
)

INVALID_LINE = "this is not a valid log line"


def test_parse_line_valid():
    record = parse_line(SAMPLE_LINE)
    assert record is not None
    assert record["remote_addr"] == "127.0.0.1"
    assert record["remote_user"] == "frank"
    assert record["method"] == "GET"
    assert record["path"] == "/apache_pb.gif"
    assert record["protocol"] == "HTTP/1.0"
    assert record["status"] == 200
    assert record["body_bytes_sent"] == 2326
    assert record["http_referer"] == "http://www.example.com/start.html"
    assert "Mozilla" in record["http_user_agent"]
    assert "timestamp" in record


def test_parse_line_invalid():
    assert parse_line(INVALID_LINE) is None


def test_parse_line_empty():
    assert parse_line("") is None
    assert parse_line("   \n") is None


def test_parse_line_no_referer():
    line = SAMPLE_LINE.replace(
        '"http://www.example.com/start.html"', '"-"'
    )
    record = parse_line(line)
    assert record is not None
    assert record["http_referer"] is None


def test_summarize_empty():
    summary = summarize([])
    assert summary["total_requests"] == 0
    assert summary["total_bytes"] == 0


def test_summarize_single_record():
    record = parse_line(SAMPLE_LINE)
    summary = summarize([record])
    assert summary["total_requests"] == 1
    assert summary["status_distribution"] == {"200": 1}
    assert summary["total_bytes"] == 2326
    assert summary["avg_bytes_per_request"] == 2326.0
    assert summary["top_paths"][0]["path"] == "/apache_pb.gif"
    assert summary["top_remote_addrs"][0]["addr"] == "127.0.0.1"


def test_summarize_multiple_records():
    records = [parse_line(SAMPLE_LINE)] * 3
    summary = summarize(records)
    assert summary["total_requests"] == 3
    assert summary["status_distribution"]["200"] == 3
    assert summary["top_paths"][0]["count"] == 3
