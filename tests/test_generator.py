"""Tests of the reusable MazeGenerator class."""

import pytest

from mazegen import ALGORITHMS, MazeGenerator

from .helpers import open_3x3, reachable, walls_coherent

SIZES = [(20, 15), (19, 15), (10, 7), (9, 7), (30, 30), (12, 9), (5, 5),
         (3, 3), (2, 1), (1, 2)]
SEEDS = range(15)


def make(width: int, height: int, seed: int, perfect: bool,
         algorithm: str = "dfs") -> MazeGenerator:
    """Build and generate a maze corner to corner."""
    gen = MazeGenerator(width, height, entry=(0, 0),
                        exit=(width - 1, height - 1), perfect=perfect,
                        seed=seed, algorithm=algorithm)
    gen.generate()
    return gen


@pytest.mark.parametrize("algorithm", ALGORITHMS)
@pytest.mark.parametrize("perfect", [True, False])
@pytest.mark.parametrize("size", SIZES)
def test_valid_structure(size: tuple[int, int], perfect: bool,
                         algorithm: str) -> None:
    """Coherent walls, closed border, full connectivity, no 3x3 area."""
    for seed in SEEDS:
        gen = make(*size, seed, perfect, algorithm)
        assert walls_coherent(gen.grid)
        free = {(x, y) for y in range(gen.height) for x in range(gen.width)
                } - set(gen.pattern_cells)
        assert reachable(gen.grid, gen.entry) == free
        assert open_3x3(gen.grid) == 0
        for x, y in gen.pattern_cells:
            assert gen.grid[y][x] == 15


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_perfect_is_a_tree(algorithm: str) -> None:
    """A perfect maze has no loop: passages = cells - 1."""
    for seed in SEEDS:
        gen = make(20, 15, seed, True, algorithm)
        assert gen.loop_count() == 0
        assert gen.dead_ends()


@pytest.mark.parametrize("algorithm", ALGORITHMS)
def test_playable_board(algorithm: str) -> None:
    """Loops, open corners and centre, only unavoidable dead ends."""
    for seed in SEEDS:
        gen = make(20, 15, seed, False, algorithm)
        assert gen.loop_count() >= 2
        for x, y in [(0, 0), (19, 0), (0, 14), (19, 14), (10, 7), (9, 7)]:
            assert gen.grid[y][x] != 15
        for dead_end in gen.dead_ends():
            # only the pockets of the "2" can force a dead end
            assert len(gen._free_neighbours(*dead_end)) < 2


def test_pattern_present_and_omitted() -> None:
    """The 42 is drawn when it fits and omitted otherwise."""
    assert make(20, 15, 1, True).has_pattern
    assert make(9, 7, 1, True).has_pattern
    assert not make(8, 8, 1, True).has_pattern
    assert not make(20, 6, 1, True).has_pattern


def test_same_seed_same_maze() -> None:
    """Reproducibility: same seed, same grid; other seed, other grid."""
    assert make(20, 15, 7, False).grid == make(20, 15, 7, False).grid
    assert make(20, 15, 7, False).grid != make(20, 15, 8, False).grid


def test_regenerate_with_seed() -> None:
    """generate(seed=...) reproduces a maze built earlier."""
    gen = make(20, 15, 5, True)
    first = [row[:] for row in gen.grid]
    gen.generate(seed=6)
    assert gen.grid != first
    gen.generate(seed=5)
    assert gen.grid == first


def test_solution_is_shortest_and_valid() -> None:
    """The path joins entry and exit and matches the cell list."""
    from .helpers import follow
    for seed in SEEDS:
        gen = make(20, 15, seed, False)
        path = gen.solve()
        assert follow(gen.grid, gen.entry, path) == gen.exit
        cells = gen.solve_cells()
        assert cells[0] == gen.entry and cells[-1] == gen.exit
        assert len(cells) == len(path) + 1


def test_big_maze_does_not_hit_recursion_limit() -> None:
    """The DFS is iterative: a large maze must not overflow the stack."""
    gen = make(200, 200, 3, True)
    assert gen.loop_count() == 0


def test_animation_callback() -> None:
    """on_step is called while carving."""
    calls: list[int] = []
    gen = MazeGenerator(8, 8, seed=1)
    gen.generate(on_step=lambda: calls.append(1))
    assert len(calls) >= 63


@pytest.mark.parametrize("kwargs", [
    {"width": 0, "height": 5},
    {"width": -3, "height": 5},
    {"width": 5, "height": 0},
    {"width": 1, "height": 1, "exit": (0, 0)},
    {"width": 5, "height": 5, "entry": (5, 0)},
    {"width": 5, "height": 5, "exit": (0, -1)},
    {"width": 5, "height": 5, "entry": (1, 1), "exit": (1, 1)},
    {"width": 20, "height": 15, "entry": (6, 5)},
    {"width": 5, "height": 5, "algorithm": "nope"},
    {"width": 5.5, "height": 5},
])
def test_invalid_parameters(kwargs: dict[str, object]) -> None:
    """Inconsistent parameters raise ValueError, never anything else."""
    with pytest.raises(ValueError):
        MazeGenerator(**kwargs)  # type: ignore[arg-type]


def test_use_before_generate() -> None:
    """Asking for a solution before generating is a clear error."""
    with pytest.raises(RuntimeError):
        MazeGenerator(5, 5).solve()
