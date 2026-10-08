"""Terminal (ANSI) rendering of the maze and the interactive menu."""

import random
import sys
import time
from dataclasses import dataclass

from mazegen import EAST, SOUTH, MazeGenerator

from .output import write_output

RESET = "\033[0m"
TILE = "  "
FRAME_DELAY = 0.01

WALL_COLOURS = (("white", 255), ("blue", 27), ("red", 196),
                ("green", 40), ("yellow", 226), ("cyan", 51),
                ("orange", 208), ("grey", 244))
PATTERN_COLOURS = (("magenta", 201), ("cyan", 51), ("orange", 208),
                   ("green", 40), ("red", 196), ("white", 255))
PATH_COLOURS = (("yellow", 226), ("cyan", 51), ("green", 46),
                ("magenta", 201), ("orange", 208), ("white", 255))
FLOOR = 16
ENTRY_COLOUR = 46
EXIT_COLOUR = 196

WALL, PATTERN, FLOOR_TILE, PATH, ENTRY, EXIT = range(6)


@dataclass
class ViewState:
    """What the user currently sees.

    Attributes:
        show_path: Whether the shortest path is drawn.
        wall: Index in ``WALL_COLOURS``.
        pattern: Index in ``PATTERN_COLOURS``.
        path: Index in ``PATH_COLOURS``.
        animate: Whether generation is animated.
    """

    show_path: bool = False
    wall: int = 0
    pattern: int = 0
    path: int = 0
    animate: bool = False


def _paint(code: int) -> str:
    """Return one tile painted with the 256-colour background ``code``."""
    return f"\033[48;5;{code}m{TILE}{RESET}"


def _touching(width: int, height: int, i: int, j: int
              ) -> list[tuple[int, int]]:
    """Return the in-bounds cells that touch the tile ``(i, j)``."""
    xs = [i // 2] if i % 2 else [i // 2 - 1, i // 2]
    ys = [j // 2] if j % 2 else [j // 2 - 1, j // 2]
    return [(x, y) for x in xs for y in ys
            if 0 <= x < width and 0 <= y < height]


def _tile_kind(maze: MazeGenerator, i: int, j: int,
               on_path: set[tuple[int, int]]) -> int:
    """Return the kind of the tile at column ``i``, row ``j``."""
    cells = _touching(maze.width, maze.height, i, j)
    in_pattern = [cell in maze.pattern_cells for cell in cells]
    if i % 2 and j % 2:  # a cell
        cell = cells[0]
        if in_pattern[0]:
            return PATTERN
        if cell == maze.entry:
            return ENTRY
        if cell == maze.exit:
            return EXIT
        return PATH if cell in on_path else FLOOR_TILE
    if i % 2 or j % 2:  # between two cells: a wall or a passage
        if len(cells) == 2:
            (ax, ay), (bx, by) = cells
            bit = EAST if ay == by else SOUTH
            if not maze.grid[ay][ax] & bit:
                both = cells[0] in on_path and cells[1] in on_path
                return PATH if both else FLOOR_TILE
    # a wall: joined to the "42" only if every cell around is part of it
    return PATTERN if all(in_pattern) else WALL


def build_tiles(maze: MazeGenerator, show_path: bool) -> list[list[int]]:
    """Build the (2H+1) x (2W+1) matrix of tile kinds of the maze.

    Cell ``(x, y)`` sits at tile ``(2x+1, 2y+1)``; the tiles between two
    cells are walls or passages, and the even/even tiles are wall corners.
    """
    path = maze.solve_cells() if show_path and maze.grid else []
    on_path = set(path)
    return [[_tile_kind(maze, i, j, on_path)
             for i in range(2 * maze.width + 1)]
            for j in range(2 * maze.height + 1)]


def render_maze(maze: MazeGenerator, view: ViewState) -> str:
    """Return the maze as a multi-line string of coloured ANSI tiles."""
    colours = {
        WALL: WALL_COLOURS[view.wall][1],
        PATTERN: PATTERN_COLOURS[view.pattern][1],
        FLOOR_TILE: FLOOR,
        PATH: PATH_COLOURS[view.path][1],
        ENTRY: ENTRY_COLOUR,
        EXIT: EXIT_COLOUR,
    }
    tiles = build_tiles(maze, view.show_path)
    return "\n".join(
        "".join(_paint(colours[kind]) for kind in row) for row in tiles)


def render_screen(maze: MazeGenerator, view: ViewState) -> str:
    """Return the header, the maze and the legend."""
    mode = "perfect" if maze.perfect else "playable (loops)"
    header = (f"A-Maze-ing  {maze.width}x{maze.height}  seed={maze.seed}  "
              f"algorithm={maze.algorithm}  mode={mode}")
    legend = (f"{_paint(ENTRY_COLOUR)} entry  {_paint(EXIT_COLOUR)} exit  "
              f"{_paint(PATH_COLOURS[view.path][1])} shortest path  "
              f"{_paint(PATTERN_COLOURS[view.pattern][1])} '42'")
    return f"{header}\n\n{render_maze(maze, view)}\n\n{legend}"


MENU = """\
  1. Re-generate a new maze
  2. Show / hide the shortest path
  3. Change wall colour
  4. Change '42' colour
  5. Change path colour
  6. Toggle generation animation
  q. Quit"""


def _clear() -> str:
    """Return the escape sequence clearing the screen (only on a tty)."""
    return "\033[H\033[2J" if sys.stdout.isatty() else ""


def _regenerate(maze: MazeGenerator, view: ViewState,
                output_file: str) -> str:
    """Generate a new maze (optionally animated) and save it.

    Returns:
        A message for the user.
    """
    seed = random.SystemRandom().randrange(2 ** 32)
    saved_path = view.show_path
    animate = view.animate and sys.stdout.isatty()
    if animate:
        view.show_path = False

        def frame() -> None:
            """Redraw the maze being carved."""
            sys.stdout.write("\033[H" + render_screen(maze, view) + "\n")
            sys.stdout.flush()
            time.sleep(FRAME_DELAY)

        sys.stdout.write("\033[H\033[2J")
        maze.generate(seed=seed, on_step=frame)
        view.show_path = saved_path
    else:
        maze.generate(seed=seed)
    try:
        write_output(maze, output_file)
    except OSError as error:
        return (f"New maze generated, but {output_file} could not be "
                f"written: {error.strerror}")
    return f"New maze generated and saved to {output_file}."


def run_menu(maze: MazeGenerator, output_file: str) -> None:
    """Display the maze and handle the user's choices until they quit.

    Ctrl+C and Ctrl+D (end of input) leave the program cleanly.
    """
    view = ViewState()
    message = ""
    while True:
        print(_clear() + render_screen(maze, view))
        print()
        print(MENU)
        if message:
            print(f"\n{message}")
        try:
            choice = input("\nChoice: ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            return
        message = ""
        if choice == "1":
            message = _regenerate(maze, view, output_file)
        elif choice == "2":
            view.show_path = not view.show_path
        elif choice == "3":
            view.wall = (view.wall + 1) % len(WALL_COLOURS)
            message = f"Wall colour: {WALL_COLOURS[view.wall][0]}"
        elif choice == "4":
            view.pattern = (view.pattern + 1) % len(PATTERN_COLOURS)
            message = f"'42' colour: {PATTERN_COLOURS[view.pattern][0]}"
        elif choice == "5":
            view.path = (view.path + 1) % len(PATH_COLOURS)
            message = f"Path colour: {PATH_COLOURS[view.path][0]}"
        elif choice == "6":
            view.animate = not view.animate
            message = f"Animation {'on' if view.animate else 'off'}"
        elif choice in ("q", "quit", "exit"):
            print("Bye!")
            return
        else:
            message = f"Unknown choice '{choice}'. Pick 1-6 or q."
