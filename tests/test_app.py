"""End-to-end tests: output file, rendering, menu and the main program."""

import sys
from pathlib import Path

import pytest

import a_maze_ing
from app.output import format_maze
from app.render import ViewState, build_tiles, render_screen, run_menu
from mazegen import MazeGenerator

from .helpers import follow, parse_output, walls_coherent


def make(perfect: bool, seed: int = 1) -> MazeGenerator:
    """A generated 20x15 maze."""
    gen = MazeGenerator(20, 15, exit=(19, 14), perfect=perfect, seed=seed)
    gen.generate()
    return gen


def test_output_format() -> None:
    """HEIGHT rows of WIDTH hex digits, blank line, entry, exit, path."""
    text = format_maze(make(False))
    assert text.endswith("\n") and "\r" not in text
    lines = text.split("\n")
    assert all(len(row) == 20 for row in lines[:15])
    assert all(c in "0123456789ABCDEF" for row in lines[:15] for c in row)
    assert lines[15] == ""
    assert lines[16] == "0,0" and lines[17] == "19,14"
    grid, entry, exit_, path = parse_output(text)
    assert walls_coherent(grid)
    assert follow(grid, entry, path) == exit_
    assert lines[19] == ""  # file ends with a single newline


def test_render_matches_grid() -> None:
    """Every passage of the grid is drawn as open, every wall as closed."""
    gen = make(False, 3)
    tiles = build_tiles(gen, True)
    assert len(tiles) == 31 and len(tiles[0]) == 41
    for y in range(15):
        for x in range(20):
            for bit, (tx, ty) in ((2, (2 * x + 2, 2 * y + 1)),
                                  (4, (2 * x + 1, 2 * y + 2))):
                drawn_open = tiles[ty][tx] in (2, 3)
                assert drawn_open == (not gen.grid[y][x] & bit)
    assert sum(row.count(3) for row in tiles) >= len(gen.solve())


def test_render_screen_has_header_and_toggle() -> None:
    """The screen shows the seed; showing the path changes the drawing."""
    gen = make(True)
    view = ViewState()
    hidden = render_screen(gen, view)
    assert f"seed={gen.seed}" in hidden
    view.show_path = True
    assert render_screen(gen, view) != hidden


def drive(monkeypatch: pytest.MonkeyPatch, answers: list[str],
          gen: MazeGenerator, out: Path) -> None:
    """Run the menu feeding ``answers`` to input()."""
    feed = iter(answers)

    def fake_input(prompt: str = "") -> str:
        """Return the next answer, EOF when exhausted."""
        try:
            return next(feed)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", fake_input)
    run_menu(gen, str(out))


def test_menu_interactions(monkeypatch: pytest.MonkeyPatch, tmp_path: Path,
                           capsys: pytest.CaptureFixture[str]) -> None:
    """Regenerate, toggle path, change colours, bad input, quit."""
    gen = make(True)
    out = tmp_path / "maze.txt"
    old_seed = gen.seed
    drive(monkeypatch, ["1", "2", "3", "4", "5", "6", "zzz", "", "q"],
          gen, out)
    assert gen.seed != old_seed
    grid, entry, exit_, path = parse_output(out.read_text())
    assert grid == gen.grid and path == gen.solve()
    shown = capsys.readouterr().out
    assert "Unknown choice" in shown and "Wall colour" in shown


def test_menu_survives_eof_and_unwritable_output(
        monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    """EOF/Ctrl+C quit cleanly; a bad output path is reported, not raised."""
    gen = make(True)
    drive(monkeypatch, [], gen, tmp_path / "x.txt")
    drive(monkeypatch, ["1"], gen, tmp_path / "missing_dir" / "x.txt")

    def interrupt(prompt: str = "") -> str:
        """Simulate Ctrl+C."""
        raise KeyboardInterrupt

    monkeypatch.setattr("builtins.input", interrupt)
    run_menu(gen, str(tmp_path / "x.txt"))


def write_config(tmp_path: Path, extra: str = "",
                 **overrides: str) -> Path:
    """Write a config file and return its path."""
    values = {"WIDTH": "20", "HEIGHT": "15", "ENTRY": "0,0",
              "EXIT": "19,14", "OUTPUT_FILE": str(tmp_path / "m.txt"),
              "PERFECT": "True"}
    values.update(overrides)
    path = tmp_path / "config.txt"
    path.write_text("".join(f"{k}={v}\n" for k, v in values.items())
                    + extra)
    return path


def test_main_end_to_end(monkeypatch: pytest.MonkeyPatch,
                         tmp_path: Path) -> None:
    """The program writes the maze, then quits from the menu."""
    config = write_config(tmp_path, "SEED=42\n")
    monkeypatch.setattr("builtins.input", lambda prompt="": "q")
    assert a_maze_ing.main(["a_maze_ing.py", str(config)]) == 0
    first = (tmp_path / "m.txt").read_text()
    assert a_maze_ing.main(["a_maze_ing.py", str(config)]) == 0
    assert (tmp_path / "m.txt").read_text() == first  # same seed


@pytest.mark.parametrize("overrides", [
    {"WIDTH": "abc"}, {"PERFECT": "yes"}, {"ENTRY": "1"},
    {"ENTRY": "50,50"}, {"ENTRY": "6,5"},
    {"OUTPUT_FILE": "/nonexistent_dir/maze.txt"},
])
def test_main_reports_errors(overrides: dict[str, str], tmp_path: Path,
                             capsys: pytest.CaptureFixture[str]) -> None:
    """Bad configurations print a clear error and return 1, no traceback."""
    config = write_config(tmp_path, **overrides)
    assert a_maze_ing.main(["a_maze_ing.py", str(config)]) == 1
    captured = capsys.readouterr()
    assert captured.err.startswith("Error:")
    assert "Traceback" not in captured.err


def test_main_usage_and_missing_file(
        capsys: pytest.CaptureFixture[str]) -> None:
    """Wrong arguments and a missing file are handled."""
    assert a_maze_ing.main(["a_maze_ing.py"]) == 2
    assert a_maze_ing.main(["a_maze_ing.py", "nope.txt"]) == 1
    assert "not found" in capsys.readouterr().err


def test_main_small_maze_warns(monkeypatch: pytest.MonkeyPatch,
                               tmp_path: Path,
                               capsys: pytest.CaptureFixture[str]) -> None:
    """A maze too small for the 42 still works and prints a message."""
    config = write_config(tmp_path, WIDTH="5", HEIGHT="5", EXIT="4,4")
    monkeypatch.setattr("builtins.input", lambda prompt="": "q")
    assert a_maze_ing.main(["a_maze_ing.py", str(config)]) == 0
    assert "'42'" in capsys.readouterr().err
    assert sys.version_info >= (3, 10)
