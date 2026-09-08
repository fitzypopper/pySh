"""Executing parsed shell commands: subprocess, pipes, and redirection."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys

from .parser import Command, ShellLine


class Executor:
    """Runs a parsed ShellLine using subprocess and pipes."""

    def __init__(self, aliases: dict[str, str]) -> None:
        self.aliases = aliases

    def run_line(self, line: ShellLine) -> int:
        pipeline = line.pipeline
        if not pipeline:
            return 0

        prev_read: int | None = None
        last_status = 0

        for idx, command in enumerate(pipeline):
            is_last = idx == len(pipeline) - 1
            prev_read, status = self._run_one(command, prev_read, is_last)
            last_status = status

        return last_status

    def _subsume(self, argv: list[str]) -> int | None:
        """Handle builtins that must run in-process. Returns exit code or None."""
        cmd = argv[0]
        if cmd == "cd":
            return self._cd(argv)
        if cmd == "exit":
            sys.exit(int(argv[1]) if len(argv) > 1 else 0)
            return 0
        if cmd == "alias" and len(argv) == 2 and "=" in argv[1]:
            name, _, value = argv[1].partition("=")
            self.aliases[name] = value
            return 0
        return None

    def _run_one(
        self, command: Command, prev_read: int | None, is_last: bool
    ) -> tuple[int | None, int]:
        argv = list(command.argv)
        if not argv:
            return prev_read, 0

        # Expand a leading alias.
        if argv[0] in self.aliases:
            expanded = shlex.split(self.aliases[argv[0]])
            argv = expanded + argv[1:]

        # Builtins that need the parent process.
        builtin = self._subsume(argv)
        if builtin is not None:
            if prev_read is not None:
                os.close(prev_read)
            return None, builtin

        try:
            resolved = shutil.which(argv[0]) or argv[0]
        except Exception:
            resolved = argv[0]

        # Set up this stage's stdin.
        stdin_fd: int | None = prev_read
        close_stdin = False
        if command.stdin_file:
            if stdin_fd is not None:
                os.close(stdin_fd)
            stdin_fd = os.open(command.stdin_file, os.O_RDONLY)
            close_stdin = True

        # Set up stdout: pipe to the next stage, or redirection, or inherit.
        next_read: int | None = None
        if not is_last:
            r, w = os.pipe()
            next_read = r
            stdout_fd = w
            close_stdout = True
        elif command.stdout_file:
            mode = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if command.stdout_append else os.O_TRUNC)
            stdout_fd = os.open(command.stdout_file, mode, 0o644)
            close_stdout = True
        else:
            stdout_fd = None
            close_stdout = False

        # Stderr redirection.
        stderr_fd: int | None = None
        close_stderr = False
        if command.stderr_file:
            mode = os.O_WRONLY | os.O_CREAT | (os.O_APPEND if command.stderr_append else os.O_TRUNC)
            stderr_fd = os.open(command.stderr_file, mode, 0o644)
            close_stderr = True

        try:
            proc = subprocess.run(
                argv,
                stdin=stdin_fd,
                stdout=stdout_fd,
                stderr=stderr_fd,
                check=False,
            )
            status = proc.returncode
        finally:
            # Close inherited file descriptors in the parent.
            if close_stdin and stdin_fd is not None:
                os.close(stdin_fd)
            if close_stdout and stdout_fd is not None:
                os.close(stdout_fd)
            if close_stderr and stderr_fd is not None:
                os.close(stderr_fd)
            if not close_stdin and prev_read is not None:
                os.close(prev_read)

        return next_read, status

    def _cd(self, argv: list[str]) -> int:
        target = argv[1] if len(argv) > 1 else os.path.expanduser("~")
        try:
            os.chdir(os.path.expanduser(target))
        except FileNotFoundError:
            print(f"cd: no such file or directory: {target}", file=sys.stderr)
            return 1
        except PermissionError:
            print(f"cd: permission denied: {target}", file=sys.stderr)
            return 1
        return 0
