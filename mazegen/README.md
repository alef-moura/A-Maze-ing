# mazegen

Reusable maze generator written in pure Python (3.10+, no dependency).

## Install

```
pip install mazegen-1.0.0-py3-none-any.whl
```

## Quick start

```python
from mazegen import MazeGenerator

gen = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14),
                    perfect=True, seed=42)
gen.generate()

print(gen.solve())          # shortest path, e.g. 'SSEEN...' (N/E/S/W)
print(gen.solve_cells())    # the same path as [(x, y), ...]
```

## Custom parameters

| Parameter   | Meaning                                                        |
|-------------|----------------------------------------------------------------|
| `width`, `height` | Maze size in cells (at least 2 cells in total)           |
| `entry`, `exit`   | `(x, y)` cells, different, inside the maze, outside the "42" |
| `perfect`   | `True`: a single path between any two cells (spanning tree). `False` (default): loop-rich board, corners and centre open, no avoidable dead end |
| `seed`      | Integer; the same seed and parameters give the same maze       |
| `algorithm` | `"dfs"` (default), `"prim"` or `"kruskal"`                     |

`generate(seed=...)` builds a new maze (with a new seed if given).
Invalid parameters raise `ValueError` with a clear message.

## Access the structure

* `gen.grid[y][x]` is an integer 0-15; a set bit is a **closed** wall:
  `1` = North, `2` = East, `4` = South, `8` = West.
  `(0, 0)` is the top-left cell. Shared walls are always coherent.
* `gen.pattern_cells`: the cells of the "42" (fully closed, value 15);
  empty when the maze is too small (`gen.has_pattern` is `False`).
* `gen.solve()` / `gen.solve_cells()`: shortest path (BFS).
* `gen.dead_ends()` and `gen.loop_count()` inspect the result.

```python
from mazegen import EAST

cell = gen.grid[0][0]
print("east wall closed" if cell & EAST else "east wall open")
```

## License

MIT, see `LICENSE.md`.
