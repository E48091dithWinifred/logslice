"""Apache Combined Log Format parser for logslice."""

import re
from datetime import datetime
from typing import Optional

# Apache Combined Log Format pattern
# Example: 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326 "http://www.example.com/start.html" "Mozilla/4.08"
APACHE_COMBINED_PATTERN = re.compile(
    r'(?P<remote_addr>\S+)\s+'
    r'(?P<ident>\S+)\s+'
    r'(?P<auth_user>\S+)\s+'
    r'\[(?P<time_local>[^\]]+)\]\s+'
    r'"(?P<request>[^"]*)"\s+'
    r'(?P<status>\d{3})\s+'
    r'(?P<body_bytes_sent>\S+)\s+'
    r'"(?P<http_referer>[^"]*)"\s+'
    r'"(?P<http_user_agent>[^"]*)"'
)

TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def parse_line(line: str) -> Optional[dict]:
    """Parse a single Apache Combined Log Format line.

    Returns a dict of parsed fields, or None if the line doesn't match.
    """
    line = line.strip()
    if not line:
        return None

    match = APACHE_COMBINED_PATTERN.match(line)
    if not match:
        return None

    data = match.groupdict()

    # Parse status code
    data["status"] = int(data["status"])

    # Parse body bytes sent (may be '-' if no body)
    raw_bytes = data["body_bytes_sent"]
    data["body_bytes_sent"] = int(raw_bytes) if raw_bytes != "-" else 0

    # Parse timestamp
    try:
        data["time_local"] = datetime.strptime(data["time_local"], TIME_FORMAT).isoformat()
    except ValueError:
        pass  # keep raw string if parsing fails

    # Parse request into method, path, protocol
    request_parts = data["request"].split(" ", 2)
    if len(request_parts) == 3:
        data["method"] = request_parts[0]
        data["path"] = request_parts[1]
        data["protocol"] = request_parts[2]
    else:
        data["method"] = None
        data["path"] = data["request"]
        data["protocol"] = None

    # Normalize dashes to None
    for key in ("ident", "auth_user", "http_referer"):
        if data.get(key) == "-":
            data[key] = None

    return data


def parse_file(path: str):
    """Yield parsed log entries from an Apache log file."""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            parsed = parse_line(line)
            if parsed is not None:
                yield parsed
