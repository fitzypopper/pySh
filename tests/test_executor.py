"""Tests for the pysh executor (subprocess, pipes, redirection)."""

import os

import pytest

from pysh.executor import Executor
from pysh.parser import parse_shell_line


def run_line(line: str) -> int:
    ex = Executor({})
    body = line[1:].strip() if line.startswith("!") else line
    parsed = parse_shell_line(body)
    return ex.run_line(parsed)


def test_simple_command(capfd):
    assert run_line("!echo hello") == 0
    out = capfd.readouterr().out
    assert out.strip() == "hello"


def test_exit_status():
    # `false` always exits 1.
    assert run_line("!false") == 1


def test_pipeline(capfd):
    assert run_line("!echo a b c | wc -w") == 0
    out = capfd.readouterr().out
    assert out.strip() == "3"


def test_pipeline_grep(capfd, tmp_path):
    src = tmp_path / "src.txt"
    src.write_text("apple\nbanana\napple pie\n")
    run_line(f"!cat {src} | grep apple")
    out = capfd.readouterr().out
    assert "apple\n" in out
    assert "apple pie" in out
    assert "banana" not in out


def test_redirection_stdout(tmp_path):
    out = tmp_path / "out.txt"
    run_line(f"!echo hello > {out}")
    assert out.read_text() == "hello\n"


def test_redirection_append(tmp_path):
    out = tmp_path / "out.txt"
    run_line(f"!echo one > {out}")
    run_line(f"!echo two >> {out}")
    assert out.read_text() == "one\ntwo\n"


def test_redirection_stdin(capfd, tmp_path):
    src = tmp_path / "in.txt"
    src.write_text("from file\n")
    run_line(f"!cat < {src}")
    assert capfd.readouterr().out == "from file\n"


def test_builtin_cd(monkeypatch, tmp_path):
    sub = tmp_path / "sub"
    sub.mkdir()
    monkeypatch.chdir(tmp_path)
    assert run_line(f"!cd {sub}") == 0
    assert os.getcwd() == str(sub)


def test_alias_expansion(capfd):
    ex = Executor({"ll": "ls -la"})
    ex.run_line(parse_shell_line("ll tests"))
    out = capfd.readouterr().out
    assert "test_" in out


def test_alias_expansion_with_args(capfd):
    src = os.path.join("tests", "test_executor.py")
    ex = Executor({"lapp": "ls"})
    ex.run_line(parse_shell_line(f"lapp {src}"))
    out = capfd.readouterr().out
    assert "test_executor.py" in out
