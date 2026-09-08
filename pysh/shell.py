"""pysh: a hybrid shell that runs Python and shell commands.

Lines starting with `!` are treated as shell commands; everything else is
evaluated as Python.
"""

from __future__ import annotations

import os
import sys

from .builtins import make_alias_fn
from .config import load_pyshrc
from .executor import Executor
from .parser import parse_shell_line


class Shell:
    """The pysh REPL."""

    def __init__(self) -> None:
        self.aliases: dict[str, str] = {}
        # A persistent namespace for evaluated Python, shared across lines.
        self.globals: dict = {
            "__name__": "__pysh__",
            "__builtins__": __builtins__,
        }
        self.executor = Executor(self.aliases)

        # Make a couple of helpers available inside Python lines.
        self.globals["alias"] = make_alias_fn(self.aliases)

    def _run_shell_line(self, body: str) -> int:
        parsed = parse_shell_line(body)
        return self.executor.run_line(parsed)

    def _run_python_line(self, body: str) -> int:
        stripped = body.strip()
        if not stripped:
            return 0
        try:
            try:
                code = compile(stripped, "<pysh>", "eval")
            except SyntaxError:
                code = compile(stripped, "<pysh>", "exec")
            result = eval(code, self.globals)
            if result is not None:
                print(repr(result))
        except SyntaxError as exc:
            print(f"SyntaxError: {exc.msg}", file=sys.stderr)
            return 1
        except Exception as exc:
            print(f"{type(exc).__name__}: {exc}", file=sys.stderr)
            return 1
        return 0

    def repl(self) -> None:
        from .readline import LineEditor, raw_mode, restore_terminal

        editor = LineEditor(prompt="> ")
        old = raw_mode()
        try:
            while True:
                line = editor.readline()
                if line == "":
                    break
                self.execute(line)
        finally:
            restore_terminal(old)

    def execute(self, line: str) -> int:
        if line.startswith("!"):
            return self._run_shell_line(line[1:].strip())
        return self._run_python_line(line)

    def run(self) -> None:
        load_pyshrc(self)
        self.repl()


def main() -> None:
    shell = Shell()
    shell.run()
