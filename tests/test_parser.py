"""Tests for the pysh parser."""

import pytest

from pysh.parser import parse_shell_line, split_tokens


def test_split_tokens_simple():
    assert split_tokens("ls -la foo") == ["ls", "-la", "foo"]


def test_split_tokens_quotes():
    assert split_tokens('echo "hello world" foo') == ["echo", "hello world", "foo"]


def test_split_tokens_empty_string():
    assert split_tokens("") == []


def test_parse_pipe():
    line = parse_shell_line("echo hi | wc -l")
    assert len(line.pipeline) == 2
    assert line.pipeline[0].argv == ["echo", "hi"]
    assert line.pipeline[1].argv == ["wc", "-l"]


def test_parse_redirect_stdout():
    line = parse_shell_line("ls > out.txt")
    assert line.pipeline[0].argv == ["ls"]
    assert line.pipeline[0].stdout_file == "out.txt"
    assert line.pipeline[0].stdout_append is False


def test_parse_redirect_append():
    line = parse_shell_line("ls >> out.txt")
    assert line.pipeline[0].stdout_file == "out.txt"
    assert line.pipeline[0].stdout_append is True


def test_parse_redirect_stdin():
    line = parse_shell_line("cat < in.txt")
    assert line.pipeline[0].stdin_file == "in.txt"


def test_parse_stderr():
    line = parse_shell_line("cmd 2> err.txt")
    assert line.pipeline[0].stderr_file == "err.txt"


def test_parse_mixed():
    line = parse_shell_line("cat < in.txt | grep foo > out.txt")
    assert line.pipeline[0].stdin_file == "in.txt"
    assert line.pipeline[1].argv == ["grep", "foo"]
    assert line.pipeline[1].stdout_file == "out.txt"
