# pysh – project notes

A hybrid shell running Python directly and shell commands via `!`.
Side project, "fun to show off" — prioritize handcrafted code over pulling
in libraries that solve everything.

See `README.md` for usage. This file records decisions and state across
sessions.

## Status (current)

MVP implemented and tested:

- [x] Raw-mode line editor (`pysh/readline.py`): termios/tty, char-by-char.
      Supports text, Enter, Backspace, Left/Right arrows. No history,
      completion, or highlighting yet.
- [x] `!cmd` parsing + subprocess execution + builtins `cd`/`exit`/`alias`
      (`pysh/executor.py`).
- [x] Pipe parser + executor (`|`) and redirection `>`, `>>`, `<`, `2>`,
      `2>>` (`pysh/parser.py`).
- [x] `.pyshrc` loaded as Python at startup (`pysh/config.py`); `alias()`
      exposed. Also respects `$PYSHRC`.
- [x] Alias system: `alias("ll", "ls -la")` defined in Python or .pyshrc;
      executor expands a leading alias token, appending remaining args.

28 pytest tests pass.

## Key design decisions

- `cd` is a builtin in-process (subprocess can't change parent cwd).
- Python lines use a persistent shared `self.globals` dict; expressions print
  their `repr` if not None; statements run via exec. Errors print a single
  clean line (no traceback).
- Executor uses `subprocess.run` with raw fds (`os.pipe`/`os.open`) for pipes
  and redirection. No pty yet, so vim/less/ssh will not behave fully.

## Delayed (future work)

- History, tab-completion, syntax highlighting.
- pty support for full interactive programs.
- Job control (`&`, `jobs`, `fg`, `bg`).
- Prompt customization (git branch, cwd styling).

## Dev

- Use `uv` for the venv/install: `uv venv .venv`
  `uv pip install --python .venv -e . pytest`
  `.venv/bin/python -m pytest`
- Interactive raw-mode cannot be driven via piped stdin (needs a real tty);
  test it through a pty (see the `pty` snippets used during development).
