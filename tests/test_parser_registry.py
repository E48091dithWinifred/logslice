"""Tests for the parser registry in logslice.parsers."""

import pytest
from logslice.parsers import get_parser, available_formats, register


def test_available_formats_includes_builtins():
    formats = available_formats()
    assert "nginx" in formats
    assert "apache" in formats


def test_get_parser_nginx():
    parser = get_parser("nginx")
    assert parser is not None
    assert callable(parser)


def test_get_parser_apache():
    parser = get_parser("apache")
    assert parser is not None
    assert callable(parser)


def test_get_parser_unknown():
    assert get_parser("nonexistent_format") is None


def test_register_custom_parser():
    def dummy_parse_file(path):
        yield {"dummy": True}

    register("dummy", dummy_parse_file)
    assert "dummy" in available_formats()
    parser = get_parser("dummy")
    assert parser is dummy_parse_file


def test_registered_parser_is_callable_with_file(tmp_path):
    """Smoke test: apache parser can be retrieved and called on a real file."""
    log_file = tmp_path / "access.log"
    log_file.write_text(
        '127.0.0.1 - - [10/Oct/2000:13:55:36 -0700] '
        '"GET / HTTP/1.1" 200 1024 "-" "TestAgent/1.0"\n',
        encoding="utf-8",
    )
    parser = get_parser("apache")
    results = list(parser(str(log_file)))
    assert len(results) == 1
    assert results[0]["status"] == 200
