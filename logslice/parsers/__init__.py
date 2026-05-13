"""Log format parsers for logslice."""

from typing import Callable, Dict, Iterator, Optional

# Registry mapping format names to their parse_file generators
_REGISTRY: Dict[str, Callable[[str], Iterator[dict]]] = {}


def register(name: str, parse_file_fn: Callable[[str], Iterator[dict]]) -> None:
    """Register a parser under the given format name."""
    _REGISTRY[name] = parse_file_fn


def get_parser(name: str) -> Optional[Callable[[str], Iterator[dict]]]:
    """Return the parse_file function for the given format name, or None."""
    return _REGISTRY.get(name)


def available_formats():
    """Return a list of registered format names."""
    return list(_REGISTRY.keys())


# Auto-register built-in parsers
def _register_builtins():
    from logslice.parsers.nginx import parse_file as nginx_parse_file
    from logslice.parsers.apache import parse_file as apache_parse_file

    register("nginx", nginx_parse_file)
    register("apache", apache_parse_file)


_register_builtins()
