"""Maze generation, solving and inspection.

The whole generator lives in the single class :class:`MazeGenerator`. A cell
is stored as an integer from 0 to 15 whose bits tell which walls are closed
(``1`` means closed): bit 0 = North, bit 1 = East, bit 2 = South, bit 3 =
West. Cells are addressed as ``grid[y][x]`` with ``(0, 0)`` at the top-left.
"""

import random
from collections import deque
from collections.abc import Callable

from .pattern import pattern_cells

NORTH = 1
EAST = 2
SOUTH = 4
WEST = 8
ALL_WALLS = NORTH | EAST | SOUTH | WEST

ALGORITHMS = ("dfs", "prim", "kruskal")

_DELTAS: dict[int, tuple[int, int]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0),
}
_OPPOSITE: dict[int, int] = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}
_LETTERS: dict[tuple[int, int], str] = {
    (0, -1): "N",
    (1, 0): "E",
    (0, 1): "S",
    (-1, 0): "W",
}


class MazeGenerator:
    """Generate a random maze, solve it and expose its structure.

    Example:
        >>> gen = MazeGenerator(20, 15, entry=(0, 0), exit=(19, 14),
        ...                     perfect=True, seed=42)
        >>> gen.generate()
        >>> gen.solve()  # doctest: +SKIP
        'SSEE...'

    Attributes:
        width: Number of columns.
        height: Number of rows.
        entry: ``(x, y)`` of the entrance.
        exit: ``(x, y)`` of the exit.
        perfect: ``True`` for a single path between any two cells.
        algorithm: Name of the carving algorithm (see ``ALGORITHMS``).
        seed: Seed used by the next call to :meth:`generate`.
        grid: ``grid[y][x]`` wall bits of every cell (empty until generated).
        pattern_cells: Cells of the "42" pattern (empty if it does not fit).
    """

    def __init__(
        self,
        width: int,
        height: int,
        entry: tuple[int, int] = (0, 0),
        exit: tuple[int, int] | None = None,
        perfect: bool = False,
        seed: int | None = None,
        algorithm: str = "dfs",
    ) -> None:
        """Validate the parameters and prepare an empty maze.

        Args:
            width: Number of columns (at least 1).
            height: Number of rows (at least 1).
            entry: ``(x, y)`` of the entrance.
            exit: ``(x, y)`` of the exit; defaults to the bottom-right cell.
            perfect: If ``True`` build a perfect maze (a spanning tree);
                otherwise build a loop-rich board with (almost) no dead end.
            seed: Seed for reproducibility; random when ``None``.
            algorithm: One of ``ALGORITHMS``.

        Raises:
            ValueError: If any parameter is inconsistent (size, coordinates
                outside the maze, entry equal to exit, entry or exit inside
                the "42" pattern, unknown algorithm).
        """
        if exit is None:
            exit = (width - 1, height - 1)
        self.width = width
        self.height = height
        self.entry = entry
        self.exit = exit
        self.perfect = perfect
        self.algorithm = algorithm
        self.seed: int = (random.SystemRandom().randrange(2 ** 32)
                          if seed is None else seed)
        self.grid: list[list[int]] = []
        self.pattern_cells: frozenset[tuple[int, int]] = frozenset()
        self._on_step: Callable[[], None] | None = None
        self._validate()
        self.pattern_cells = pattern_cells(width, height)
        for name, cell in (("entry", entry), ("exit", exit)):
            if cell in self.pattern_cells:
                raise ValueError(
                    f"{name} {cell} is inside the '42' pattern")

    # ------------------------------------------------------------------
    # validation
    # ------------------------------------------------------------------
    def _validate(self) -> None:
        """Check the constructor parameters."""
        for name, value in (("width", self.width), ("height", self.height)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise ValueError(f"{name} must be an integer")
            if value < 1:
                raise ValueError(f"{name} must be at least 1, got {value}")
        if self.width * self.height < 2:
            raise ValueError("the maze needs at least 2 cells")
        for name, cell in (("entry", self.entry), ("exit", self.exit)):
            if (len(cell) != 2
                    or not all(isinstance(v, int) for v in cell)):
                raise ValueError(f"{name} must be a pair of integers")
            if not self._in_bounds(*cell):
                raise ValueError(
                    f"{name} {cell} is outside the {self.width}x"
                    f"{self.height} maze")
        if self.entry == self.exit:
            raise ValueError("entry and exit must be different cells")
        if self.algorithm not in ALGORITHMS:
            raise ValueError(
                f"unknown algorithm '{self.algorithm}' "
                f"(choose from: {', '.join(ALGORITHMS)})")

    # ------------------------------------------------------------------
    # public API
    # ------------------------------------------------------------------
    @property
    def has_pattern(self) -> bool:
        """Whether the "42" pattern fits in this maze."""
        return bool(self.pattern_cells)

    def generate(
        self,
        seed: int | None = None,
        on_step: Callable[[], None] | None = None,
    ) -> None:
        """Generate a new maze in ``self.grid``.

        Args:
            seed: Optional new seed. The same seed always gives the same
                maze for the same parameters.
            on_step: Optional callback invoked after every wall removed, to
                animate the generation.
        """
        if seed is not None:
            self.seed = seed
        rng = random.Random(self.seed)
        self._on_step = on_step
        try:
            self._reset()
            self._carve(rng)
            if not self.perfect:
                self._braid(rng)
        finally:
            self._on_step = None

    def solve_cells(self) -> list[tuple[int, int]]:
        """Return the shortest path from entry to exit as a list of cells.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """
        self._require_grid()
        parents: dict[tuple[int, int], tuple[int, int] | None] = {
            self.entry: None}
        queue: deque[tuple[int, int]] = deque([self.entry])
        while queue:
            cell = queue.popleft()
            if cell == self.exit:
                break
            x, y = cell
            for direction, (dx, dy) in _DELTAS.items():
                nxt = (x + dx, y + dy)
                if (not self.grid[y][x] & direction
                        and nxt not in parents):
                    parents[nxt] = cell
                    queue.append(nxt)
        path: list[tuple[int, int]] = []
        node: tuple[int, int] | None = self.exit
        while node is not None:
            path.append(node)
            node = parents[node]
        path.reverse()
        return path

    def solve(self) -> str:
        """Return the shortest path from entry to exit as ``N/E/S/W`` text.

        Raises:
            RuntimeError: If the maze has not been generated yet.
        """
        cells = self.solve_cells()
        return "".join(
            _LETTERS[(bx - ax, by - ay)]
            for (ax, ay), (bx, by) in zip(cells, cells[1:]))

    def dead_ends(self) -> list[tuple[int, int]]:
        """Return the cells (outside the "42") with exactly one opening."""
        self._require_grid()
        return [(x, y)
                for y in range(self.height) for x in range(self.width)
                if (x, y) not in self.pattern_cells
                and bin(self.grid[y][x]).count("1") == 3]

    def loop_count(self) -> int:
        """Return the number of independent loops (0 for a perfect maze)."""
        self._require_grid()
        free = self.width * self.height - len(self.pattern_cells)
        passages = sum(
            (not cell & EAST) + (not cell & SOUTH)
            for row in self.grid for cell in row)
        return passages - free + 1

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------
    def _require_grid(self) -> None:
        """Raise if :meth:`generate` has not been called yet."""
        if not self.grid:
            raise RuntimeError("the maze has not been generated yet")

    def _in_bounds(self, x: int, y: int) -> bool:
        """Tell whether ``(x, y)`` is inside the maze."""
        return 0 <= x < self.width and 0 <= y < self.height

    def _is_free(self, x: int, y: int) -> bool:
        """Tell whether ``(x, y)`` is inside the maze and not a "42" cell."""
        return self._in_bounds(x, y) and (x, y) not in self.pattern_cells

    def _free_neighbours(
            self, x: int, y: int) -> list[tuple[int, int, int]]:
        """Return ``(nx, ny, direction)`` for every free neighbour."""
        result = []
        for direction, (dx, dy) in _DELTAS.items():
            if self._is_free(x + dx, y + dy):
                result.append((x + dx, y + dy, direction))
        return result

    def _reset(self) -> None:
        """Close every wall of every cell."""
        self.grid = [[ALL_WALLS] * self.width for _ in range(self.height)]

    def _open(self, x: int, y: int, direction: int) -> None:
        """Remove the wall between ``(x, y)`` and its neighbour.

        Both cells are updated, which keeps shared walls coherent.
        """
        dx, dy = _DELTAS[direction]
        self.grid[y][x] &= ~direction
        self.grid[y + dy][x + dx] &= ~_OPPOSITE[direction]

    def _close(self, x: int, y: int, direction: int) -> None:
        """Put back the wall between ``(x, y)`` and its neighbour."""
        dx, dy = _DELTAS[direction]
        self.grid[y][x] |= direction
        self.grid[y + dy][x + dx] |= _OPPOSITE[direction]

    def _step(self) -> None:
        """Notify the animation callback, if any."""
        if self._on_step is not None:
            self._on_step()

    # ------------------------------------------------------------------
    # carving algorithms (each one builds a spanning tree)
    # ------------------------------------------------------------------
    def _carve(self, rng: random.Random) -> None:
        """Build a spanning tree of the free cells with the chosen algorithm.

        Raises:
            RuntimeError: If some free cells could not be reached.
        """
        carvers = {
            "dfs": self._carve_dfs,
            "prim": self._carve_prim,
            "kruskal": self._carve_kruskal,
        }
        carved = carvers[self.algorithm](rng)
        free = self.width * self.height - len(self.pattern_cells)
        if carved != free:
            raise RuntimeError("could not connect every cell of the maze")

    def _carve_dfs(self, rng: random.Random) -> int:
        """Recursive backtracker with an explicit stack (no recursion)."""
        visited = {self.entry}
        stack = [self.entry]
        while stack:
            x, y = stack[-1]
            options = [n for n in self._free_neighbours(x, y)
                       if (n[0], n[1]) not in visited]
            if not options:
                stack.pop()
                continue
            nx, ny, direction = rng.choice(options)
            self._open(x, y, direction)
            visited.add((nx, ny))
            stack.append((nx, ny))
            self._step()
        return len(visited)

    def _carve_prim(self, rng: random.Random) -> int:
        """Randomised Prim: grow the maze from a random frontier edge."""
        visited = {self.entry}
        frontier = [(self.entry[0], self.entry[1], n[2])
                    for n in self._free_neighbours(*self.entry)]
        while frontier:
            index = rng.randrange(len(frontier))
            frontier[index], frontier[-1] = frontier[-1], frontier[index]
            x, y, direction = frontier.pop()
            dx, dy = _DELTAS[direction]
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            self._open(x, y, direction)
            visited.add((nx, ny))
            frontier.extend(
                (nx, ny, n[2]) for n in self._free_neighbours(nx, ny)
                if (n[0], n[1]) not in visited)
            self._step()
        return len(visited)

    def _carve_kruskal(self, rng: random.Random) -> int:
        """Randomised Kruskal: join sets of cells with shuffled edges."""
        parent: dict[tuple[int, int], tuple[int, int]] = {}
        edges: list[tuple[int, int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                if (x, y) in self.pattern_cells:
                    continue
                parent[(x, y)] = (x, y)
                for nx, ny, direction in self._free_neighbours(x, y):
                    if direction in (EAST, SOUTH):
                        edges.append((x, y, direction))
        rng.shuffle(edges)

        def find(cell: tuple[int, int]) -> tuple[int, int]:
            """Return the representative of the set holding ``cell``."""
            while parent[cell] != cell:
                parent[cell] = parent[parent[cell]]
                cell = parent[cell]
            return cell

        joined = 1
        for x, y, direction in edges:
            dx, dy = _DELTAS[direction]
            root_a, root_b = find((x, y)), find((x + dx, y + dy))
            if root_a == root_b:
                continue
            parent[root_a] = root_b
            self._open(x, y, direction)
            joined += 1
            self._step()
        return joined

    # ------------------------------------------------------------------
    # braiding (turns the perfect maze into a loop-rich board)
    # ------------------------------------------------------------------
    def _open_block_near(self, x: int, y: int) -> bool:
        """Tell whether a fully open 3x3 window contains ``(x, y)``."""
        for left in range(x - 2, x + 1):
            for top in range(y - 2, y + 1):
                if self._window_open(left, top):
                    return True
        return False

    def _window_open(self, left: int, top: int) -> bool:
        """Tell whether the 3x3 window at ``(left, top)`` has no inner wall."""
        if (left < 0 or top < 0
                or left + 3 > self.width or top + 3 > self.height):
            return False
        for j in range(3):
            for i in range(3):
                cell = self.grid[top + j][left + i]
                if (i < 2 and cell & EAST) or (j < 2 and cell & SOUTH):
                    return False
        return True

    def _braid(self, rng: random.Random) -> None:
        """Remove dead ends by opening walls, never creating a 3x3 block."""
        progress = True
        while progress:
            progress = False
            dead_ends = self.dead_ends()
            rng.shuffle(dead_ends)
            for x, y in dead_ends:
                if bin(self.grid[y][x]).count("1") != 3:
                    continue
                candidates = [n for n in self._free_neighbours(x, y)
                              if self.grid[y][x] & n[2]]
                rng.shuffle(candidates)
                candidates.sort(
                    key=lambda n: bin(self.grid[n[1]][n[0]]).count("1") != 3)
                for nx, ny, direction in candidates:
                    self._open(x, y, direction)
                    if (self._open_block_near(x, y)
                            or self._open_block_near(nx, ny)):
                        self._close(x, y, direction)
                        continue
                    progress = True
                    self._step()
                    break
