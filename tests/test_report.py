"""Tests for logslice.report."""

from logslice.report import build_report


SAMPLE_RECORDS = [
    {"ip": "10.0.0.1", "method": "GET", "path": "/index", "status": "200", "response_time": 0.1},
    {"ip": "10.0.0.2", "method": "POST", "path": "/api", "status": "201", "response_time": 0.3},
    {"ip": "10.0.0.1", "method": "GET", "path": "/index", "status": "404", "response_time": 0.05},
    {"ip": "10.0.0.3", "method": "GET", "path": "/about", "status": "500", "response_time": 1.2},
    {"ip": "10.0.0.1", "method": "GET", "path": "/index", "status": "200", "response_time": 0.08},
]


def test_build_report_total_requests():
    report = build_report(SAMPLE_RECORDS)
    assert report["total_requests"] == 5


def test_build_report_status_counts():
    report = build_report(SAMPLE_RECORDS)
    assert report["status_counts"]["200"] == 2
    assert report["status_counts"]["404"] == 1
    assert report["status_counts"]["500"] == 1


def test_build_report_error_rate():
    report = build_report(SAMPLE_RECORDS)
    # 2 errors (404, 500) out of 5 requests = 0.4
    assert abs(report["error_rate"] - 0.4) < 1e-4


def test_build_report_top_ips():
    report = build_report(SAMPLE_RECORDS)
    top_ip = report["top_ips"][0]
    assert top_ip["value"] == "10.0.0.1"
    assert top_ip["count"] == 3


def test_build_report_top_paths():
    report = build_report(SAMPLE_RECORDS)
    assert report["top_paths"][0]["value"] == "/index"


def test_build_report_response_time_stats_present():
    report = build_report(SAMPLE_RECORDS)
    rt = report["response_time_stats"]
    assert "min" in rt and "max" in rt and "mean" in rt
    assert rt["min"] == 0.05
    assert rt["max"] == 1.2


def test_build_report_empty_records():
    report = build_report([])
    assert report["total_requests"] == 0
    assert report["error_rate"] == 0.0
    assert report["top_ips"] == []
    assert report["response_time_stats"]["mean"] == 0.0


def test_build_report_top_n_respected():
    report = build_report(SAMPLE_RECORDS, top=1)
    assert len(report["top_ips"]) == 1
    assert len(report["top_paths"]) == 1
