"""Loading .pyshrc at startup.

The .pyshrc file is executed as Python code with access to the shell object.
Conventional setup looks like:

    alias("ll", "ls -la")

because `alias` is made available as a global during startup.
"""

from __future__ import annotations

import os
import shlex


def find_pyshrc() -> str | None:
    """Look for $PYSHRC or ~/.pyshrc."""
    path = os.environ.get("PYSHRC")
    if path and os.path.exists(path):
        return path
    home = os.path.expanduser("~")
    candidate = os.path.join(home, ".pyshrc")
    if os.path.exists(candidate):
        return candidate
    return None


def load_pyshrc(shell) -> None:
    """Execute the user's .pyshrc as Python inside the provided globals."""
    path = find_pyshrc()
    if not path:
        return
    try:
        with open(path, encoding="utf-8") as f:
            code = f.read()
    except OSError as exc:
        print(f"pysh: could not read {path}: {exc}", file=os.sys.stderr)
        return
    try:
        exec(code, shell.globals)
    except Exception as exc:
        print(f"pysh: error in {path}: {exc}", file=os.sys.stderr)
