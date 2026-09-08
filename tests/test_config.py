"""Tests for .pyshrc config loading."""

from pysh.config import load_pyshrc
from pysh.shell import Shell


def test_load_pyshrc(tmp_path, monkeypatch):
    rc = tmp_path / ".pyshrc"
    rc.write_text('alias("ll", "ls -la")\nVALUE = 42\n')
    monkeypatch.setenv("PYSHRC", str(rc))

    s = Shell()
    load_pyshrc(s)
    assert s.aliases["ll"] == "ls -la"
    assert s.globals["VALUE"] == 42


def test_no_pyshrc(tmp_path, monkeypatch):
    # Point PYSHRC at a nonexistent file; should not raise.
    monkeypatch.setenv("PYSHRC", str(tmp_path / "missing"))
    s = Shell()
    load_pyshrc(s)  # must not raise
    assert s.aliases == {}
