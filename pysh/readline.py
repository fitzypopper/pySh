"""Readline for pysh: a hand-written raw-mode line editor.

Reads input character-by-character using termios/tty. Supports plain text,
Enter, Backspace, and arrow-key movement as a minimal MVP. History and tab
completion are out of scope for the MVP.
"""

from __future__ import annotations

import sys
import termios
import tty


class LineEditor:
    """A small line editor driven by raw terminal input."""

    def __init__(self, prompt: str = "> ") -> None:
        self.prompt = prompt
        # The current buffer and the cursor position (index into buffer).
        self.buffer: list[str] = []
        self.cursor = 0

    def _echo(self) -> None:
        """Redraw the current line, placing the cursor at `self.cursor`."""
        line = self.prompt + "".join(self.buffer)
        # Clear the line, rewrite it, then move the cursor back.
        sys.stdout.write("\r\x1b[2K" + line)
        sys.stdout.write("\r\x1b[" + str(len(self.prompt) + self.cursor + 1) + "G")
        sys.stdout.flush()

    def _insert(self, ch: str) -> None:
        self.buffer.insert(self.cursor, ch)
        self.cursor += 1

    def _delete_before(self) -> None:
        """Backspace: remove the character before the cursor."""
        if self.cursor > 0:
            del self.buffer[self.cursor - 1]
            self.cursor -= 1

    def _handle_escape(self) -> None:
        """Read the rest of an escape sequence (arrows)."""
        seq = sys.stdin.read(1)
        if seq == "[":
            key = sys.stdin.read(1)
            if key == "D" and self.cursor > 0:      # Left arrow
                self.cursor -= 1
            elif key == "C" and self.cursor < len(self.buffer):  # Right arrow
                self.cursor += 1
        # Up/Down (A/B) are ignored for the MVP.

    def readline(self) -> str:
        """Read one line, returning it without the trailing newline."""
        sys.stdout.write(self.prompt)
        sys.stdout.flush()

        while True:
            ch = sys.stdin.read(1)
            if not ch:
                # EOF.
                if self.buffer:
                    line = "".join(self.buffer)
                    self.buffer = []
                    self.cursor = 0
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return line
                return ""
            if ch == "\n" or ch == "\r":
                sys.stdout.write("\n")
                sys.stdout.flush()
                line = "".join(self.buffer)
                self.buffer = []
                self.cursor = 0
                return line
            elif ch == "\x7f":  # Backspace (DEL)
                self._delete_before()
                self._echo()
            elif ch == "\x1b":  # Escape sequence (arrows etc.)
                self._handle_escape()
                self._echo()
            elif ch == "\x04":  # Ctrl-D at empty line -> EOF
                if not self.buffer:
                    sys.stdout.write("\n")
                    sys.stdout.flush()
                    return ""
                continue
            elif ord(ch) >= 32:
                self._insert(ch)
                self._echo()


def raw_mode() -> list:
    """Enable raw mode for stdin so we can read keys one at a time.

    Returns the previous terminal attributes so the caller can restore them.
    """
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    tty.setraw(fd)
    return old


def restore_terminal(old: list) -> None:
    """Restore the terminal attributes captured by raw_mode()."""
    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
