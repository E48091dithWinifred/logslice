"""Parser for Nginx combined log format."""

import re
from datetime import datetime
from typing import Optional

NGINX_COMBINED_PATTERN = re.compile(
    r'(?P<remote_addr>\S+) '
    r'\S+ '
    r'(?P<remote_user>\S+) '
    r'\[(?P<time_local>[^\]]+)\] '
    r'"(?P<method>\S+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) '
    r'(?P<body_bytes_sent>\d+) '
    r'"(?P<http_referer>[^"]*)" '
    r'"(?P<http_user_agent>[^"]*)"'
)

TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def parse_line(line: str) -> Optional[dict]:
    """Parse a single Nginx log line into a structured dict.

    Returns None if the line does not match the expected format.
    """
    line = line.strip()
    if not line:
        return None

    match = NGINX_COMBINED_PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()

    try:
        data["timestamp"] = datetime.strptime(
            data.pop("time_local"), TIME_FORMAT
        ).isoformat()
    except ValueError:
        data["timestamp"] = data.pop("time_local")

    data["status"] = int(data["status"])
    data["body_bytes_sent"] = int(data["body_bytes_sent"])

    if data["remote_user"] == "-":
        data["remote_user"] = None
    if data["http_referer"] == "-":
        data["http_referer"] = None

    return data


def parse_file(filepath: str) -> list[dict]:
    """Parse an entire Nginx log file and return a list of parsed records."""
    records = []
    with open(filepath, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            record = parse_line(line)
            if record is not None:
                records.append(record)
    return records
