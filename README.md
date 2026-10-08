*This project has been created as part of the 42 curriculum by alesferr and ahideo-k.*

# A-Maze-ing

## Description

A-Maze-ing generates a random maze from a configuration file, saves it in a
hexadecimal wall format and displays it in the terminal with an interactive
menu. The maze generation lives in a standalone, reusable package
(`mazegen`) that can be installed with `pip`.

Overview:

* **Two modes.** `PERFECT=True` builds a perfect maze (exactly one path
  between any two cells). `PERFECT=False` builds a board usable by a
  Pac-Man-like game: fully connected, open corners and centre, many loops,
  and no avoidable dead end.
* **"42" pattern** drawn with fully closed cells (omitted, with a message
  on the console, when the maze is too small).
* **Reproducible**: the same `SEED` gives the same maze.
* **Shortest path** (BFS) written in the output file and shown on demand.
* **Bonuses**: three generation algorithms, generation animation, and a
  braided default mode without avoidable dead ends.

## Instructions

Requirements: Python 3.10 or later.

```
make install     # creates .venv and installs flake8, mypy, pytest, build
make run         # python3 a_maze_ing.py config.txt
make debug       # same, under pdb
make lint        # flake8 + mypy (mandatory flags)
make lint-strict # flake8 + mypy --strict
make test        # pytest
make build       # rebuilds mazegen-*.whl / .tar.gz and copies them to the root
make clean       # removes caches and build directories
```

Without `make`:

```
python3 a_maze_ing.py config.txt
```

The program needs no third-party package. The generated maze is written to
`OUTPUT_FILE` (it is rewritten every time a new maze is generated from the
menu, so the file always matches what is displayed).

### Interactive menu

| Key | Action |
|-----|--------|
| `1` | Re-generate a new maze (new random seed, shown in the header) |
| `2` | Show / hide the shortest path from entry to exit |
| `3` | Change the wall colour |
| `4` | Change the colour of the "42" pattern |
| `5` | Change the path colour |
| `6` | Toggle the generation animation |
| `q` | Quit (Ctrl+C and Ctrl+D also quit cleanly) |

Legend: green = entry, red = exit, coloured cells = "42", highlighted
line = shortest path.

### Error handling

Every error (missing file, bad syntax, impossible parameters, unwritable
output) prints `Error: <explanation>` on stderr and exits with status 1,
without a traceback.

## Configuration file

One `KEY=VALUE` pair per line. Empty lines and lines starting with `#` are
ignored. Keys are case-insensitive. Spaces around keys and values are
ignored.

| Key | Required | Meaning | Example |
|-----|----------|---------|---------|
| `WIDTH` | yes | Number of columns, 1 to 200 | `WIDTH=20` |
| `HEIGHT` | yes | Number of rows, 1 to 200 | `HEIGHT=15` |
| `ENTRY` | yes | Entry cell `x,y` (`0,0` is the top-left cell) | `ENTRY=0,0` |
| `EXIT` | yes | Exit cell `x,y`, different from the entry | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | Path of the output file | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `True` or `False` (any letter case) | `PERFECT=False` |
| `SEED` | no | Non-negative integer; random if absent | `SEED=42` |
| `ALGORITHM` | no | `dfs` (default), `prim` or `kruskal` | `ALGORITHM=prim` |

Rules: entry and exit must be inside the maze, different, and outside the
"42" pattern. A duplicate key or a value of the wrong type is an error; an
unknown key only prints a warning and is ignored. A default file,
`config.txt`, is provided.

### Output file format

One hexadecimal digit per cell, one row per line. Bit 0 = North, bit 1 =
East, bit 2 = South, bit 3 = West; a bit set to 1 means the wall is
**closed** (`A` = `1010` = east and west walls closed). After the rows come
an empty line, the entry (`x,y`), the exit (`x,y`) and the shortest path as
`N`, `E`, `S`, `W` letters. All lines end with `\n`.

## Maze generation

### Algorithm

1. **Carving** with the *recursive backtracker* (depth-first search),
   implemented with an explicit stack, not recursion. It produces a
   spanning tree: every cell is reachable and there is exactly one path
   between two cells. `PERFECT=True` stops here.
2. **Braiding** (`PERFECT=False`): every dead end gets one more opening,
   preferably towards another dead end, and an opening is refused if it
   would create a fully open 3x3 area. The result has many independent
   loops and no avoidable dead end. Only the pockets of the "2" in the
   "42" can force a dead end (no free neighbour to open towards).
3. **Solving** with a breadth-first search, which gives the shortest path.

`prim` and `kruskal` are alternative carving algorithms (bonus); steps 2
and 3 are identical.

### Why this algorithm

The backtracker is simple to explain and to verify, creates long winding
corridors (a good "maze" feel) and, being a spanning tree, guarantees
connectivity, a single path and the absence of open areas. Braiding adds
the loops required by the playable mode without a second generator, and the
3x3 check keeps corridors at most 2 cells wide.

## Reusable module (`mazegen`)

Everything is in the `MazeGenerator` class (`mazegen/generator.py`),
packaged as `mazegen-1.0.0-py3-none-any.whl` (and `.tar.gz`) at the root of
the repository. The module knows nothing about the configuration file, the
terminal or the output format; `a_maze_ing.py` and the `app/` folder are
the (non-reusable) application built on top of it.

```
pip install mazegen-1.0.0-py3-none-any.whl
```

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14),
                    perfect=True, seed=42)
gen.generate()
print(gen.solve())         # e.g. 'EESENEEESE...' shortest path (N/E/S/W)
print(gen.solve_cells())   # same path as [(x, y), ...]
```

* **Custom parameters**: `width`, `height`, `entry`, `exit`, `perfect`,
  `seed`, `algorithm` (`"dfs"`, `"prim"`, `"kruskal"`). Invalid values raise
  `ValueError`. `gen.generate(seed=...)` builds another maze.
* **Structure**: `gen.grid[y][x]` is an integer 0-15 (bits `1` N, `2` E,
  `4` S, `8` W, set = closed wall; `(0, 0)` is the top-left cell);
  `gen.pattern_cells` holds the "42" cells; `gen.dead_ends()` and
  `gen.loop_count()` describe the result.
* **Solution**: `gen.solve()` (letters) and `gen.solve_cells()` (cells).

To rebuild the package from the sources (in a virtualenv):

```
pip install build
python -m build            # creates dist/mazegen-1.0.0*
```

The license (MIT, `LICENSE.md`) explicitly allows reusing and distributing
the generator in later projects.

## Resources

* [Maze generation algorithms](https://en.wikipedia.org/wiki/Maze_generation_algorithm)
  (Wikipedia: backtracker, Prim, Kruskal, spanning trees).
* [Mazes for Programmers](https://pragprog.com/titles/jbmaze/mazes-for-programmers/)
  by Jamis Buck (braiding, dead ends, Prim, Kruskal).
* [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search).
* [Python documentation](https://docs.python.org/3/): `random`, `collections`,
  `dataclasses`, `typing`.
* [PEP 8](https://peps.python.org/pep-0008/),
  [PEP 257](https://peps.python.org/pep-0257/),
  [mypy](https://mypy.readthedocs.io/), [flake8](https://flake8.pycqa.org/).
* [Python Packaging User Guide](https://packaging.python.org/).
* [ANSI escape codes](https://en.wikipedia.org/wiki/ANSI_escape_code).
* `docs/estudo.html`: study guide (in Portuguese) explaining, for a
  complete beginner, every concept used in this project.

### Use of AI

<!-- TODO: review and adjust this section so it is true for your team. -->
AI (Claude Code) was used to: read the subject and the evaluation sheet and
draft the implementation plan; write a first version of the code, the unit
tests, the Makefile and the packaging files; and write the study guide
`docs/estudo.html`. Every generated part was reviewed, run, linted and
tested by the team, and the team can explain it.

## Team and project management

<!-- TODO: fill in with the real information of your team. -->

* **Roles**: <login1>: TODO. <login2>: TODO.
* **Planning**: the plan was split into phases (skeleton and tooling,
  configuration parser, generator, "42" pattern, braided mode, display and
  menu, packaging, README, bonuses, study guide, defence rehearsal).
  TODO: describe how it evolved.
* **What worked well / could be improved**: TODO.
* **Tools**: Python 3, flake8, mypy, pytest, `build`, Make, Git, Claude Code
  (see "Use of AI"). TODO: add the others.
