"""Tests for logslice.filters module."""

from datetime import datetime
import pytest
from logslice.filters import (
    filter_by_status,
    filter_by_status_range,
    filter_by_method,
    filter_by_ip,
    filter_by_path_prefix,
    filter_by_date_range,
    build_filter_chain,
)

SAMPLE_ENTRIES = [
    {"ip": "1.2.3.4", "method": "GET", "path": "/home", "status": 200,
     "timestamp": datetime(2024, 1, 15, 10, 0, 0)},
    {"ip": "5.6.7.8", "method": "POST", "path": "/api/data", "status": 201,
     "timestamp": datetime(2024, 1, 15, 11, 0, 0)},
    {"ip": "1.2.3.4", "method": "GET", "path": "/api/users", "status": 404,
     "timestamp": datetime(2024, 1, 16, 9, 0, 0)},
    {"ip": "9.9.9.9", "method": "DELETE", "path": "/admin", "status": 403,
     "timestamp": datetime(2024, 1, 16, 12, 0, 0)},
    {"ip": "5.6.7.8", "method": "GET", "path": "/home", "status": 500,
     "timestamp": datetime(2024, 1, 17, 8, 0, 0)},
]


def test_filter_by_status_match():
    result = filter_by_status(SAMPLE_ENTRIES, 200)
    assert len(result) == 1
    assert result[0]["path"] == "/home"


def test_filter_by_status_no_match():
    result = filter_by_status(SAMPLE_ENTRIES, 301)
    assert result == []


def test_filter_by_status_range():
    result = filter_by_status_range(SAMPLE_ENTRIES, 200, 299)
    assert len(result) == 2
    assert all(200 <= e["status"] <= 299 for e in result)


def test_filter_by_method_get():
    result = filter_by_method(SAMPLE_ENTRIES, "GET")
    assert len(result) == 3


def test_filter_by_method_case_insensitive():
    result = filter_by_method(SAMPLE_ENTRIES, "post")
    assert len(result) == 1
    assert result[0]["status"] == 201


def test_filter_by_ip():
    result = filter_by_ip(SAMPLE_ENTRIES, "1.2.3.4")
    assert len(result) == 2


def test_filter_by_path_prefix():
    result = filter_by_path_prefix(SAMPLE_ENTRIES, "/api")
    assert len(result) == 2
    assert all(e["path"].startswith("/api") for e in result)


def test_filter_by_date_range_both_bounds():
    start = datetime(2024, 1, 15, 0, 0, 0)
    end = datetime(2024, 1, 15, 23, 59, 59)
    result = filter_by_date_range(SAMPLE_ENTRIES, start=start, end=end)
    assert len(result) == 2


def test_filter_by_date_range_no_bounds():
    result = filter_by_date_range(SAMPLE_ENTRIES)
    assert len(result) == len(SAMPLE_ENTRIES)


def test_filter_by_date_range_skips_missing_timestamp():
    entries = [{"ip": "1.1.1.1", "status": 200}]
    result = filter_by_date_range(entries, start=datetime(2024, 1, 1))
    assert result == []


def test_build_filter_chain():
    chain = build_filter_chain([
        lambda e: filter_by_method(e, "GET"),
        lambda e: filter_by_status_range(e, 200, 299),
    ])
    result = chain(SAMPLE_ENTRIES)
    assert len(result) == 1
    assert result[0]["path"] == "/home"
    assert result[0]["status"] == 200


def test_build_filter_chain_empty():
    chain = build_filter_chain([])
    result = chain(SAMPLE_ENTRIES)
    assert result == SAMPLE_ENTRIES
