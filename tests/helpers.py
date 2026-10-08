"""Independent maze checks shared by the tests (they read raw hex rows)."""

from collections import deque

N, E, S, W = 1, 2, 4, 8
DELTAS = {N: (0, -1), E: (1, 0), S: (0, 1), W: (-1, 0)}
OPPOSITE = {N: S, S: N, E: W, W: E}


def parse_output(text: str) -> tuple[list[list[int]], tuple[int, int],
                                     tuple[int, int], str]:
    """Parse an output file into (grid, entry, exit, path)."""
    lines = text.split("\n")
    blank = lines.index("")
    grid = [[int(c, 16) for c in row] for row in lines[:blank]]
    entry = tuple(int(v) for v in lines[blank + 1].split(","))
    exit_ = tuple(int(v) for v in lines[blank + 2].split(","))
    return grid, (entry[0], entry[1]), (exit_[0], exit_[1]), lines[blank + 3]


def walls_coherent(grid: list[list[int]]) -> bool:
    """Every shared wall is encoded the same way by both cells."""
    height, width = len(grid), len(grid[0])
    for y in range(height):
        for x in range(width):
            for bit, (dx, dy) in DELTAS.items():
                nx, ny = x + dx, y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    if not grid[y][x] & bit:
                        return False  # the border must be closed
                elif bool(grid[y][x] & bit) != bool(
                        grid[ny][nx] & OPPOSITE[bit]):
                    return False
    return True


def reachable(grid: list[list[int]],
              start: tuple[int, int]) -> set[tuple[int, int]]:
    """Cells reachable from ``start`` through open passages."""
    seen = {start}
    queue = deque([start])
    while queue:
        x, y = queue.popleft()
        for bit, (dx, dy) in DELTAS.items():
            nxt = (x + dx, y + dy)
            if not grid[y][x] & bit and nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return seen


def open_3x3(grid: list[list[int]]) -> int:
    """Count the 3x3 windows without any inner wall."""
    height, width = len(grid), len(grid[0])
    count = 0
    for top in range(height - 2):
        for left in range(width - 2):
            if all(
                not ((i < 2 and grid[top + j][left + i] & E)
                     or (j < 2 and grid[top + j][left + i] & S))
                for j in range(3) for i in range(3)
            ):
                count += 1
    return count


def follow(grid: list[list[int]], start: tuple[int, int],
           path: str) -> tuple[int, int] | None:
    """Walk ``path`` from ``start``; ``None`` if it crosses a wall."""
    letters = {"N": N, "E": E, "S": S, "W": W}
    x, y = start
    for letter in path:
        bit = letters[letter]
        if grid[y][x] & bit:
            return None
        dx, dy = DELTAS[bit]
        x, y = x + dx, y + dy
    return x, y
