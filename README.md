# logslice

A fast log file parser and aggregator that outputs structured JSON summaries for common log formats.

---

## Installation

```bash
pip install logslice
```

Or install from source:

```bash
git clone https://github.com/yourname/logslice.git && cd logslice && pip install .
```

---

## Usage

Parse a log file and output a structured JSON summary:

```bash
logslice parse access.log --format nginx
```

Use it directly in Python:

```python
from logslice import LogParser

parser = LogParser(format="nginx")
summary = parser.parse("access.log")

print(summary)
# {
#   "total_requests": 4821,
#   "error_rate": 0.03,
#   "top_ips": ["192.168.1.1", "10.0.0.5"],
#   "status_codes": {"200": 4672, "404": 98, "500": 51}
# }
```

### Supported Formats

| Format   | Flag         |
|----------|--------------|
| Nginx    | `--format nginx`   |
| Apache   | `--format apache`  |
| Syslog   | `--format syslog`  |
| JSON logs | `--format json`   |

### Options

```
--format    Log format to parse (default: nginx)
--output    Output file path (default: stdout)
--since     Filter entries after a timestamp
--level     Filter by log level (error, warn, info)
```

---

## License

This project is licensed under the [MIT License](LICENSE).