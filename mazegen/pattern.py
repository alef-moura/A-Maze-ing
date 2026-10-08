"""Layout of the "42" pattern drawn with fully closed cells."""

DIGIT_WIDTH = 3
DIGIT_HEIGHT = 5
MARGIN = 1

_FOUR = ("X..", "X..", "XXX", "..X", "..X")
_TWO = ("XXX", "..X", "XXX", "X..", "XXX")


def pattern_cells(width: int, height: int) -> frozenset[tuple[int, int]]:
    """Return the cells forming the "42" pattern, centred in the maze.

    The two digits are separated by a gap of one column (odd width) or two
    columns (even width), so that the gap is always centred on the middle
    column(s) of the maze and the centre of the maze stays an open corridor.

    Args:
        width: Maze width in cells.
        height: Maze height in cells.

    Returns:
        The set of ``(x, y)`` cells that must stay fully closed, or an empty
        set when the maze is too small to hold the pattern with a free margin
        of one cell all around it.
    """
    gap = 1 if width % 2 else 2
    block_width = 2 * DIGIT_WIDTH + gap
    if (width < block_width + 2 * MARGIN
            or height < DIGIT_HEIGHT + 2 * MARGIN):
        return frozenset()
    left = (width - block_width) // 2
    top = (height - DIGIT_HEIGHT) // 2
    cells: set[tuple[int, int]] = set()
    for row in range(DIGIT_HEIGHT):
        for col in range(DIGIT_WIDTH):
            if _FOUR[row][col] == "X":
                cells.add((left + col, top + row))
            if _TWO[row][col] == "X":
                cells.add((left + DIGIT_WIDTH + gap + col, top + row))
    return frozenset(cells)
