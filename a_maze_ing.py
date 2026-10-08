"""A-Maze-ing: generate, save and display a maze.

Usage: python3 a_maze_ing.py config.txt
"""

import sys

from app.config import ConfigError, load_config
from app.output import write_output
from app.render import run_menu
from mazegen import MazeGenerator


def run(config_path: str) -> int:
    """Load the config, generate the maze, save it and show the menu.

    Args:
        config_path: Path of the configuration file.

    Returns:
        The process exit code (0 on success, 1 on a reported error).
    """
    try:
        config = load_config(config_path)
        maze = MazeGenerator(
            width=config.width,
            height=config.height,
            entry=config.entry,
            exit=config.exit,
            perfect=config.perfect,
            seed=config.seed,
            algorithm=config.algorithm,
        )
    except (ConfigError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    if not maze.has_pattern:
        print("Error: the maze is too small to draw the '42' pattern; "
              "it was omitted.", file=sys.stderr)
    maze.generate()
    try:
        write_output(maze, config.output_file)
    except OSError as error:
        print(f"Error: cannot write {config.output_file}: {error.strerror}",
              file=sys.stderr)
        return 1
    print(f"Maze saved to {config.output_file} (seed {maze.seed}).")
    run_menu(maze, config.output_file)
    return 0


def main(argv: list[str]) -> int:
    """Program entry point; never lets an exception escape.

    Args:
        argv: Command-line arguments, including the program name.

    Returns:
        The process exit code.
    """
    if len(argv) != 2:
        print("Usage: python3 a_maze_ing.py config.txt", file=sys.stderr)
        return 2
    try:
        return run(argv[1])
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        return 130
    except Exception as error:  # last-resort safety net
        print(f"Error: unexpected failure ({type(error).__name__}: "
              f"{error})", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
