"""Built-in commands for pysh.

Most builtins are handled directly in the executor, but this module exposes
helpers that make .pyshrc setup ergonomic (e.g. the `alias(...)` function).
"""

from __future__ import annotations


def make_alias_fn(aliases: dict[str, str]):
    """Return an `alias(name, value)` callable bound to the shell's alias map."""

    def alias(name: str, value: str) -> None:
        aliases[name] = value

    return alias
