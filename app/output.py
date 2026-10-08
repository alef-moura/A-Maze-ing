"""Writing of the maze output file (hexadecimal wall encoding)."""

from mazegen import MazeGenerator


def format_maze(maze: MazeGenerator) -> str:
    """Return the content of the output file for a generated maze.

    One hexadecimal digit per cell (bit 0 = North, 1 = East, 2 = South,
    3 = West; a set bit is a closed wall), one row per line, then an empty
    line, the entry, the exit and the shortest path as ``N/E/S/W`` letters.
    Every line ends with a newline.
    """
    rows = ["".join(format(cell, "X") for cell in row) for row in maze.grid]
    return (
        "\n".join(rows) + "\n\n"
        f"{maze.entry[0]},{maze.entry[1]}\n"
        f"{maze.exit[0]},{maze.exit[1]}\n"
        f"{maze.solve()}\n"
    )


def write_output(maze: MazeGenerator, path: str) -> None:
    """Write the maze to ``path``.

    Raises:
        OSError: If the file cannot be written.
    """
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        handle.write(format_maze(maze))
