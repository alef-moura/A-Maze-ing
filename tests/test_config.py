"""Tests of the configuration parser (the error cases of the evaluation)."""

from pathlib import Path

import pytest

from app.config import ConfigError, load_config, parse_lines

GOOD = [
    "# comment",
    "WIDTH=20",
    "HEIGHT=15",
    "ENTRY=0,0",
    "EXIT=19,14",
    "OUTPUT_FILE=maze.txt",
    "PERFECT=True",
]


def without(key: str) -> list[str]:
    """GOOD without the line of ``key``."""
    return [line for line in GOOD if not line.startswith(key)]


def replaced(key: str, value: str) -> list[str]:
    """GOOD with ``key`` set to ``value``."""
    return [f"{key}={value}" if line.startswith(key + "=") else line
            for line in GOOD]


def test_valid_config() -> None:
    """A correct file gives the expected settings."""
    config = parse_lines(GOOD)
    assert (config.width, config.height) == (20, 15)
    assert config.entry == (0, 0) and config.exit == (19, 14)
    assert config.perfect is True and config.seed is None
    assert config.algorithm == "dfs"


def test_lowercase_keys_and_spaces() -> None:
    """Keys are case-insensitive; spaces around values are tolerated."""
    config = parse_lines(["width = 5", "Height=5", "entry= 0, 0",
                          "exit=4 ,4", "output_file=o.txt",
                          "perfect=false", "seed=3", "algorithm=PRIM"])
    assert config.exit == (4, 4) and config.perfect is False
    assert config.seed == 3 and config.algorithm == "prim"


@pytest.mark.parametrize("key", ["WIDTH", "HEIGHT", "ENTRY", "EXIT",
                                 "OUTPUT_FILE", "PERFECT"])
def test_missing_key(key: str) -> None:
    """Removing a mandatory key is reported."""
    with pytest.raises(ConfigError, match=key):
        parse_lines(without(key))


def test_line_without_equal_sign() -> None:
    """A line that is not KEY=VALUE is rejected with its number."""
    with pytest.raises(ConfigError, match="line 3"):
        parse_lines(GOOD[:2] + ["HEIGHT 15"] + GOOD[3:])


@pytest.mark.parametrize("key,value", [
    ("WIDTH", "abc"), ("WIDTH", "1.5"), ("WIDTH", ""), ("WIDTH", "0"),
    ("WIDTH", "-4"), ("WIDTH", "99999"), ("HEIGHT", "ten"),
    ("PERFECT", "maybe"), ("PERFECT", "1"), ("PERFECT", ""),
    ("ENTRY", "0"), ("ENTRY", "0,0,0"), ("ENTRY", "a,b"),
    ("ENTRY", "(0,0)"), ("ENTRY", "0;0"), ("EXIT", "1,"),
    ("ENTRY", "20,0"), ("EXIT", "19,15"), ("EXIT", "-1,3"),
    ("EXIT", "0,0"), ("SEED", "x"), ("SEED", "-1"),
    ("ALGORITHM", "dijkstra"),
])
def test_bad_values(key: str, value: str) -> None:
    """Letters, wrong tuples, bad booleans, out-of-range cells."""
    with pytest.raises(ConfigError):
        parse_lines(replaced(key, value) if key in
                    ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "PERFECT")
                    else GOOD + [f"{key}={value}"])


def test_duplicate_and_unknown_keys(capsys: pytest.CaptureFixture[str]
                                    ) -> None:
    """Duplicates are errors; unknown keys only produce a warning."""
    with pytest.raises(ConfigError, match="duplicate"):
        parse_lines(GOOD + ["WIDTH=5"])
    parse_lines(GOOD + ["COLOR=red"])
    assert "unknown key COLOR" in capsys.readouterr().err


def test_load_config_errors(tmp_path: Path) -> None:
    """Missing file, directory and binary file give ConfigError."""
    with pytest.raises(ConfigError, match="not found"):
        load_config(str(tmp_path / "nope.txt"))
    with pytest.raises(ConfigError):
        load_config(str(tmp_path))
    binary = tmp_path / "bin.txt"
    binary.write_bytes(b"\xff\xfe\x00\x80")
    with pytest.raises(ConfigError):
        load_config(str(binary))


def test_load_config_file(tmp_path: Path) -> None:
    """A real file with Windows line endings is accepted."""
    path = tmp_path / "c.txt"
    path.write_bytes("\r\n".join(GOOD).encode())
    assert load_config(str(path)).width == 20
