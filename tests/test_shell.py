"""Tests for the pysh shell-level behavior (Python eval/exec, aliases)."""

from pysh.shell import Shell


def test_python_eval(capfd):
    s = Shell()
    assert s.execute("1 + 2") == 0
    assert capfd.readouterr().out.strip() == "3"


def test_python_exec_no_output(capfd):
    s = Shell()
    assert s.execute("x = 10") == 0
    assert capfd.readouterr().out == ""


def test_python_namespace_persists(capfd):
    s = Shell()
    s.execute("x = 10")
    assert s.execute("x * 3") == 0
    assert capfd.readouterr().out.strip() == "30"


def test_python_runtime_error(capfd):
    s = Shell()
    assert s.execute("1 / 0") == 1
    err = capfd.readouterr().err
    assert "ZeroDivisionError" in err


def test_python_syntax_error(capfd):
    s = Shell()
    assert s.execute("1 0") == 1
    assert "SyntaxError" in capfd.readouterr().err


def test_alias_via_python():
    s = Shell()
    assert s.execute('alias("ll", "ls -la")') == 0
    assert s.aliases["ll"] == "ls -la"


def test_shell_line_dispatch_same_as_execute(capfd):
    s = Shell()
    assert s.execute("!echo shell") == 0
    assert capfd.readouterr().out.strip() == "shell"
