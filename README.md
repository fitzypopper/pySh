# pysh

A hybrid shell: run Python directly, and shell commands through `!`.

## Ideas

- Lines starting with `!` are shell commands (subprocess, with pipes and
  redirection).
- Any other line is evaluated as Python, with a persistent namespace.
- `cd` is a builtin so it persists in the parent shell process.
- A `.pyshrc` file runs as Python at startup (`alias()` is available).

## Status

MVP focusing on the core loop and parsing. Missing (by design, for now):
history, tab-completion, syntax highlighting, pty support for full
interactive programs (vim/less/ssh), and job control.

## Install

```
pip install -e .
```

## Usage

```
$ pysh
> 1 + 2
3
> !ls -la
> !echo hi | wc -c
> !cd Projects
> alias("ll", "ls -la")
```

`.pyshrc` example (in `~/.pyshrc`): both forms work there since it runs as Python.

## Development

```
pytest
```
