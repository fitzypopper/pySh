"""Parsing for pysh.

Splits an input line into one of two kinds of command:
  - shell command (starts with `!`) with optional pipes and redirection
  - python code (anything else)

For shell commands, we tokenize the command line into a sequence of
`Command` fragments separated by `|`, where each fragment may carry
input/output redirection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Redirection:
    """A single redirection directive on a command fragment."""

    kind: str          # ">" | ">>" | "<"
    target: str        # file path


@dataclass
class Command:
    """One pipeline stage: argv plus any redirections."""

    argv: list[str] = field(default_factory=list)
    stdin_file: Optional[str] = None
    stdout_file: Optional[str] = None
    stdout_append: bool = False
    stderr_file: Optional[str] = None
    stderr_append: bool = False


@dataclass
class ShellLine:
    """A parsed shell line."""

    pipeline: list[Command]
    # cwd to use (set by `cd` builtin which stays in the parent);
    # None means "don't change".
    pipefail: bool = False


def split_tokens(line: str) -> list[str]:
    """Split a line into shell tokens, respecting single/double quotes.

    Quotes are removed once the token is formed.
    """
    tokens = []
    current: list[str] = []
    quote = None  # "'" or '"' when inside quotes
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if quote:
            if ch == quote:
                quote = None
            else:
                current.append(ch)
            i += 1
            continue
        if ch in ("'", '"'):
            quote = ch
            i += 1
            continue
        if ch.isspace():
            if current:
                tokens.append("".join(current))
                current = []
            i += 1
            continue
        current.append(ch)
        i += 1
    if current:
        tokens.append("".join(current))
    return tokens


def parse_shell_line(line: str) -> ShellLine:
    """Parse a `!`-command line, producing a pipeline of Commands."""
    tokens = split_tokens(line)
    pipeline: list[Command] = []
    current = Command()

    def push_current() -> None:
        nonlocal current
        if current.argv or (
            current.stdin_file
            or current.stdout_file
            or current.stderr_file
        ):
            pipeline.append(current)
            current = Command()

    i = 0
    while i < len(tokens):
        tok = tokens[i]
        if tok in ("|", "||", "&&"):
            push_current()
            i += 1
            continue
        elif tok in (">", ">>", "<", "2>", "2>>"):
            kind = tok[0]
            append = ">>" in tok
            i += 1
            if i >= len(tokens):
                target = ""
            else:
                target = tokens[i]
                i += 1
            if tok.startswith("2"):
                current.stderr_file = target
                current.stderr_append = append
            elif kind == ">":
                current.stdout_file = target
                current.stdout_append = append
            elif kind == "<":
                current.stdin_file = target
        else:
            current.argv.append(tok)
            i += 1
    push_current()
    return ShellLine(pipeline=pipeline)
