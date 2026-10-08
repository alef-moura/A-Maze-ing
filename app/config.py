"""Parsing and validation of the configuration file."""

import re
import sys
from collections.abc import Iterable
from dataclasses import dataclass

from mazegen import ALGORITHMS

MANDATORY_KEYS = ("WIDTH", "HEIGHT", "ENTRY", "EXIT", "OUTPUT_FILE",
                  "PERFECT")
OPTIONAL_KEYS = ("SEED", "ALGORITHM")
MAX_SIZE = 200

_INT = re.compile(r"-?[0-9]+")
_PAIR = re.compile(r"\s*(-?[0-9]+)\s*,\s*(-?[0-9]+)\s*")


class ConfigError(Exception):
    """Raised when the configuration file is missing or invalid."""


@dataclass(frozen=True)
class MazeConfig:
    """Validated maze settings.

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: ``(x, y)`` of the entrance.
        exit: ``(x, y)`` of the exit.
        output_file: Path of the file receiving the maze.
        perfect: ``True`` to build a perfect maze.
        seed: Seed for reproducibility, ``None`` for a random one.
        algorithm: Carving algorithm name.
    """

    width: int
    height: int
    entry: tuple[int, int]
    exit: tuple[int, int]
    output_file: str
    perfect: bool
    seed: int | None = None
    algorithm: str = "dfs"


def _parse_int(key: str, value: str) -> int:
    """Convert ``value`` to an integer or raise a clear ``ConfigError``."""
    if not _INT.fullmatch(value):
        raise ConfigError(f"{key} must be an integer, got '{value}'")
    return int(value)


def _parse_size(key: str, value: str) -> int:
    """Parse a WIDTH/HEIGHT value (positive, bounded)."""
    number = _parse_int(key, value)
    if not 1 <= number <= MAX_SIZE:
        raise ConfigError(
            f"{key} must be between 1 and {MAX_SIZE}, got {number}")
    return number


def _parse_pair(key: str, value: str) -> tuple[int, int]:
    """Parse an ``x,y`` coordinate pair."""
    match = _PAIR.fullmatch(value)
    if match is None:
        raise ConfigError(
            f"{key} must look like 'x,y' (two integers), got '{value}'")
    return int(match.group(1)), int(match.group(2))


def _parse_bool(key: str, value: str) -> bool:
    """Parse ``True`` / ``False`` (any letter case)."""
    lowered = value.lower()
    if lowered not in ("true", "false"):
        raise ConfigError(f"{key} must be True or False, got '{value}'")
    return lowered == "true"


def _read_pairs(lines: Iterable[str]) -> dict[str, str]:
    """Turn the raw lines into a ``KEY -> value`` dictionary."""
    pairs: dict[str, str] = {}
    for number, raw in enumerate(lines, start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            raise ConfigError(
                f"line {number}: expected KEY=VALUE, got '{line}'")
        key, value = line.split("=", 1)
        key = key.strip().upper()
        value = value.strip()
        if not key:
            raise ConfigError(f"line {number}: empty key before '='")
        if key in pairs:
            raise ConfigError(f"line {number}: duplicate key {key}")
        if not value:
            raise ConfigError(f"line {number}: {key} has no value")
        if key not in MANDATORY_KEYS + OPTIONAL_KEYS:
            print(f"Warning: line {number}: unknown key {key} ignored",
                  file=sys.stderr)
            continue
        pairs[key] = value
    return pairs


def _check_cell(key: str, cell: tuple[int, int],
                width: int, height: int) -> None:
    """Make sure ``cell`` lies inside the maze."""
    if not (0 <= cell[0] < width and 0 <= cell[1] < height):
        raise ConfigError(
            f"{key}={cell[0]},{cell[1]} is outside the {width}x{height} "
            f"maze (x in 0..{width - 1}, y in 0..{height - 1})")


def parse_lines(lines: Iterable[str]) -> MazeConfig:
    """Parse configuration lines into a validated :class:`MazeConfig`.

    Args:
        lines: The lines of the configuration file.

    Returns:
        The validated settings.

    Raises:
        ConfigError: On any syntax or consistency problem.
    """
    pairs = _read_pairs(lines)
    missing = [key for key in MANDATORY_KEYS if key not in pairs]
    if missing:
        raise ConfigError(f"missing mandatory key(s): {', '.join(missing)}")
    width = _parse_size("WIDTH", pairs["WIDTH"])
    height = _parse_size("HEIGHT", pairs["HEIGHT"])
    entry = _parse_pair("ENTRY", pairs["ENTRY"])
    exit_ = _parse_pair("EXIT", pairs["EXIT"])
    _check_cell("ENTRY", entry, width, height)
    _check_cell("EXIT", exit_, width, height)
    if entry == exit_:
        raise ConfigError("ENTRY and EXIT must be different cells")
    if width * height < 2:
        raise ConfigError("the maze needs at least 2 cells")
    seed = None
    if "SEED" in pairs:
        seed = _parse_int("SEED", pairs["SEED"])
        if seed < 0:
            raise ConfigError(f"SEED must not be negative, got {seed}")
    algorithm = pairs.get("ALGORITHM", "dfs").lower()
    if algorithm not in ALGORITHMS:
        raise ConfigError(
            f"ALGORITHM must be one of {', '.join(ALGORITHMS)}, "
            f"got '{pairs['ALGORITHM']}'")
    return MazeConfig(
        width=width,
        height=height,
        entry=entry,
        exit=exit_,
        output_file=pairs["OUTPUT_FILE"],
        perfect=_parse_bool("PERFECT", pairs["PERFECT"]),
        seed=seed,
        algorithm=algorithm,
    )


def load_config(path: str) -> MazeConfig:
    """Read and parse the configuration file at ``path``.

    Raises:
        ConfigError: If the file cannot be read or its content is invalid.
    """
    try:
        with open(path, encoding="utf-8-sig") as handle:
            lines = handle.read().splitlines()
    except FileNotFoundError:
        raise ConfigError(f"configuration file not found: {path}") from None
    except UnicodeDecodeError:
        raise ConfigError(
            f"{path} is not a valid UTF-8 text file") from None
    except OSError as error:
        raise ConfigError(f"cannot read {path}: {error.strerror}") from None
    return parse_lines(lines)
