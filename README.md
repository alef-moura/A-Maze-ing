*This project has been created as part of the 42 curriculum by alesferr and edgda-si.*


# A-Maze-ing

## Table of Contents

- [Description](#description)
- [Features](#features)
- [Getting Started](#getting-started)
- [Configuration File](#configuration-file)
- [Interactive Menu](#interactive-menu)
- [Maze Generation](#maze-generation)
- [Understanding the Maze Structure](#understanding-the-maze-structure)
- [Output File Format](#output-file-format)
- [Reusable Module: mazegen](#reusable-module-mazegen)
- [Technical Notes & Validation](#technical-notes--validation)
- [Project Structure](#project-structure)
- [Resources](#resources)
- [Team and Project Management](#team-and-project-management)

---

## Description

**A-Maze-ing** is a Python project developed as part of the 42 curriculum. Its goal is to create a maze generator capable of building random, valid mazes from a configuration file, displaying them in the terminal, and exporting their structure to a file using hexadecimal wall encoding.

The project explores fundamental computer science concepts, including graph theory, maze-generation algorithms, randomization, pathfinding, data structures, Python packaging, and code reusability.

The generation engine is implemented as a standalone Python package called `mazegen`, which can be installed and reused independently in other projects.

The application supports two different maze-generation modes:

- **Perfect Maze:** a maze with no loops, where exactly one path exists between any two reachable cells.
- **Playable Maze:** a fully connected board with multiple independent routes, designed for a Pac-Man-like game.

The generated maze includes a visual representation of the number **42**, the entrance and exit positions, and the shortest path connecting them.

### How it works

The application follows this general workflow:

```text
       CONFIGURATION FILE
              |
              v
       Read and validate
        configuration
              |
              v
       Generate the maze
              |
              v
        Draw the "42"
              |
              v
       Create maze mode
       PERFECT = True/False
              |
              v
       Calculate shortest
             path
              |
              v
       Save hexadecimal
        output file
              |
              v
       Display maze and
       interactive menu
```

## Features

| Feature | Description |
|---|---|
| Random generation | Creates a different maze using randomization. |
| Reproducibility | Generates the same maze when the same seed and parameters are used. |
| Perfect maze | Generates a maze without loops. |
| Playable maze | Generates a connected board with multiple independent routes. |
| Three algorithms | Supports DFS, Prim's and Kruskal's algorithms. |
| 42 pattern | Draws the number 42 using fully closed cells. |
| Shortest path | Calculates the shortest route using Breadth-First Search (BFS). |
| Terminal rendering | Displays walls, entrance, exit, pattern and solution. |
| Interactive menu | Allows users to generate mazes and change display options. |
| Generation animation | Offers an animated visualization of the generation process. |
| Reusable package | Provides an independently installable `mazegen` package. |
| Error handling | Validates configuration parameters and handles errors without unexpected tracebacks. |

---

## Getting Started

### Requirements

- Python 3.10 or later.
- `pip`.
- `make` (recommended for using the provided commands).

The maze application itself does not require third-party Python packages. Development and testing tools are installed separately.

### Installation

Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```

Install the development dependencies and create the virtual environment:

```bash
make install
```

This command creates a `.venv` environment and installs the tools used by the project, including:

- `flake8` — code style verification.
- `mypy` — static type checking.
- `pytest` — automated tests.
- `build` — Python package building.

### Running the application

Use the default configuration file:

```bash
make run
```

Or execute the main script directly:

```bash
python3 a_maze_ing.py config.txt
```

The program reads the configuration, generates a maze, displays it in the terminal and saves it to the configured output file.

### Available Makefile commands

| Command | Description |
|---|---|
| `make install` | Creates the virtual environment and installs development dependencies. |
| `make run` | Executes the main application. |
| `make debug` | Executes the application using Python's debugger (`pdb`). |
| `make lint` | Runs flake8 and mypy with the required flags. |
| `make lint-strict` | Runs flake8 and mypy in strict mode. |
| `make test` | Runs automated tests using pytest. |
| `make build` | Builds the reusable package in `.whl` and `.tar.gz` formats and copies the artifacts to the repository root. |
| `make clean` | Removes temporary files, caches and build directories. |

To execute the debugger directly:

```bash
python3 -m pdb a_maze_ing.py config.txt
```

---

## Configuration File

The maze is configured through a plain-text file containing one `KEY=VALUE` pair per line.

The default configuration file is `config.txt`.

### Configuration format

```ini
# Maze dimensions
WIDTH=20
HEIGHT=15

# Entrance and exit coordinates
ENTRY=0,0
EXIT=19,14

# Output file
OUTPUT_FILE=maze.txt

# Generation mode
PERFECT=False

# Optional parameters
SEED=42
ALGORITHM=dfs
```

### Configuration parameters

| Key | Required | Description | Example |
|---|---|---|---|
| `WIDTH` | Yes | Number of columns in the maze. Valid range: 1–200. | `WIDTH=20` |
| `HEIGHT` | Yes | Number of rows in the maze. Valid range: 1–200. | `HEIGHT=15` |
| `ENTRY` | Yes | Coordinates of the entrance, in `x,y` format. | `ENTRY=0,0` |
| `EXIT` | Yes | Coordinates of the exit, in `x,y` format. | `EXIT=19,14` |
| `OUTPUT_FILE` | Yes | Path where the generated maze will be saved. | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | Yes | Defines whether the maze must be perfect. Accepts `True` or `False`, regardless of letter case. | `PERFECT=False` |
| `SEED` | No | Non-negative integer used to reproduce a maze. If omitted, a random seed is used. | `SEED=42` |
| `ALGORITHM` | No | Generation algorithm: `dfs`, `prim` or `kruskal`. Default: `dfs`. | `ALGORITHM=prim` |

### Understanding coordinates

Coordinates use the following convention:

- `x` represents the column (horizontal position).
- `y` represents the row (vertical position).
- The first cell is `(0,0)`, located in the upper-left corner.
- Coordinates increase from left to right and from top to bottom.

Example for a maze with `WIDTH=5` and `HEIGHT=4`:

```text
        x = 0   1   2   3   4

y = 0      A   A   A   A   A
y = 1      A   .   .   .   A
y = 2      A   .   .   .   A
y = 3      A   A   A   A   A
```

`A` represents a cell position in the grid, not a wall encoding.

### Configuration rules

- Each line must follow the `KEY=VALUE` format.
- Lines beginning with `#` are comments and are ignored.
- Empty lines are ignored.
- Keys are case-insensitive.
- Spaces around keys and values are ignored.
- All six mandatory parameters must be present.
- `ENTRY` and `EXIT` must be inside the maze boundaries.
- Entrance and exit must be different.
- Both positions must be outside the 42 pattern.
- Duplicate keys and invalid values generate errors.
- Unknown keys generate a warning and are ignored.
- If the maze is too small to contain the 42 pattern, the pattern is omitted and a message is printed.

### Example of invalid configurations

```ini
WIDTH=abc
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=False
```

The value `abc` is invalid because `WIDTH` expects an integer.

Other examples of invalid parameters:

```ini
PERFECT=maybe
ENTRY=0
EXIT=200,14
SEED=-10
```

The application must report configuration errors clearly, without unexpected crashes or Python tracebacks.

---

## Interactive Menu

After generating the maze, the application displays an interactive menu.

| Key | Action |
|---|---|
| `1` | Generate a new random maze. |
| `2` | Show or hide the shortest path. |
| `3` | Change wall colours. |
| `4` | Change the colour of the 42 pattern. |
| `5` | Change the shortest-path colour. |
| `6` | Enable or disable generation animation. |
| `q` | Quit the application. |

The application also handles `Ctrl+C` and `Ctrl+D` as clean exit commands.

### Visual legend

- **Green:** entrance.
- **Red:** exit.
- **Coloured cells:** 42 pattern.
- **Highlighted line:** shortest path.
- **Walls:** maze boundaries and internal barriers.

The output file is updated whenever a new maze is generated, keeping the saved structure synchronized with the displayed maze.

---

## Maze Generation

The project implements three algorithms for generating the initial maze structure:

1. Depth-First Search (DFS), also known as Recursive Backtracker.
2. Prim's Algorithm.
3. Kruskal's Algorithm.

DFS is the default algorithm.

After the initial carving process, the application applies the selected generation mode and calculates the shortest path.

### 1. Depth-First Search (DFS) — Recursive Backtracker

DFS explores the maze by moving from one cell to an unvisited neighbouring cell.

The algorithm uses a stack to remember the exploration path.

**How it works:**

1. Start at a selected cell.
2. Mark the current cell as visited.
3. Find its unvisited neighbours.
4. Randomly choose one neighbour.
5. Remove the wall between the current cell and the selected neighbour.
6. Move to that neighbour and repeat the process.
7. If no unvisited neighbours remain, return to the previous cell using the stack.
8. Continue until every reachable cell has been visited.

The implementation uses an explicit stack instead of recursive function calls, avoiding recursion-depth limitations.

**Simplified flow:**

```text
        START
          |
          v
     Choose a cell
          |
          v
     Mark as visited
          |
          v
   Find unvisited neighbours
          |
          v
   Are there neighbours?
       /       \
     YES        NO
      |          |
      v          v
  Choose one   Is stack empty?
  randomly      /      \
      |        NO       YES
      v         |        |
 Remove wall    v        v
      |       Backtrack  END
      v
 Move to neighbour
      |
      └──── Repeat
```

Because each new cell is connected to the existing maze through exactly one opening, the resulting structure is a spanning tree.

A spanning tree connects every vertex without creating cycles.

This property makes DFS particularly suitable for generating perfect mazes.

### 2. Prim's Algorithm

Prim's algorithm builds a maze by expanding a connected region.

**General idea:**

1. Start with an initial cell.
2. Add its neighbouring walls to a list.
3. Randomly select a wall from that list.
4. If the wall connects a visited cell to an unvisited cell, remove it.
5. Add the newly reached cell's walls to the list.
6. Repeat until all cells are connected.

The algorithm creates a spanning tree, just like DFS, but uses a different exploration strategy.

### 3. Kruskal's Algorithm

Kruskal's algorithm starts with individual disconnected cells and progressively connects them.

**General idea:**

1. Consider every cell as an independent component.
2. Create a list of walls between neighbouring cells.
3. Shuffle the walls randomly.
4. Select a wall.
5. Check whether the cells on each side belong to different components.
6. If they do, remove the wall and merge the components.
7. Continue until all cells belong to one connected component.

This process avoids cycles by connecting only different components.

### Comparison of the algorithms

| Algorithm | Main data structure / technique | General behaviour |
|---|---|---|
| DFS | Explicit stack | Long, winding corridors and deep exploration. |
| Prim | Frontier wall list | Expands the maze from its existing boundary. |
| Kruskal | Disjoint sets / component merging | Connects independent regions without creating cycles. |

All three algorithms generate the initial connected structure. The subsequent processing determines the final maze mode.

---

### Perfect Maze — `PERFECT=True`

A perfect maze has exactly one possible path between any two cells.

This means:

- Every reachable cell is connected.
- There are no loops.
- There is only one route between two different cells.
- Dead ends are naturally present.
- The structure is equivalent to a spanning tree.

**Conceptual representation:**

```text
+---+---+---+
|       |   |
+---+   +   +
|   |       |
+   +---+   +
|           |
+---+---+---+
```

The maze remains in its original spanning-tree structure after carving.

### Playable Maze — `PERFECT=False`

The default mode creates a board suitable for a Pac-Man-like game.

Unlike a perfect maze, this mode needs alternative routes so that the player can escape when being chased.

Its requirements include:

- Full connectivity: every corridor must be reachable.
- The four corners must be open corridors.
- The centre must be an open corridor.
- At least two independent routes must exist.
- Dead ends should be rare, although a few are tolerated.
- No open area of 3×3 cells or larger is allowed.

The project uses a process called **braiding** to introduce additional openings into the initial maze.

### Braiding: creating alternative routes

Braiding reduces dead ends by opening additional walls.

The implementation follows this general process:

1. Identify dead-end cells.
2. Find available neighbouring cells.
3. Prefer openings that connect to other dead ends.
4. Remove a suitable wall to create an alternative route.
5. Check that the opening does not create a completely open 3×3 area.
6. Repeat until the dead ends have been addressed as far as possible.

The 42 pattern consists of fully closed cells, so some surrounding pockets may have no available neighbour to open. These can still result in unavoidable dead ends.

**Why avoid open 3×3 areas?**

A completely open 3×3 area would create an excessively large open space, which is forbidden by the project requirements.

The braiding process therefore checks the surrounding cells before accepting an opening.

### Perfect vs. Playable

| Property | `PERFECT=True` | `PERFECT=False` |
|---|---|---|
| Connected | Yes | Yes |
| Loops | None | Multiple |
| Unique path between cells | Yes | Not necessarily |
| Dead ends | Naturally present | Rare; a few tolerated |
| Alternative routes | No | Yes |
| Pac-Man-like gameplay | No | Yes |
| Braiding | No | Yes |

---

### Shortest Path — Breadth-First Search (BFS)

After generating the maze, the application calculates the shortest path between the entrance and exit.

The algorithm used is **Breadth-First Search (BFS)**.

BFS explores neighbouring cells level by level, starting from the entrance.

It first visits all cells one step away, then all cells two steps away, and continues until the exit is reached.

Because each movement between adjacent cells has the same cost, BFS guarantees the shortest path.

**How it works:**

1. Add the entrance to a queue.
2. Mark the entrance as visited.
3. Remove the first cell from the queue.
4. Check its accessible neighbours.
5. Add each unvisited neighbour to the queue.
6. Store the previous cell for each newly visited cell.
7. Continue until the exit is reached.
8. Reconstruct the route by following the stored previous cells backwards.

**Important concepts:**

- **Queue:** follows FIFO (First In, First Out).
- **Visited:** prevents revisiting cells.
- **Predecessor:** stores the previous cell, allowing the path to be reconstructed.
- **Directions:** the final route is represented using `N`, `E`, `S` and `W`.

```text
         ENTRY
           |
           v
      Initialize queue
           |
           v
      Explore neighbours
           |
           v
      Mark visited cells
           |
           v
       EXIT reached?
        /       \
      NO         YES
      |           |
      v           v
   Continue    Reconstruct
   searching     shortest
                   path
                    |
                    v
                   END
```

The application provides two ways to access the solution:

- `solve()` returns the path as a sequence of direction letters.
- `solve_cells()` returns the path as a list of cell coordinates.

---

## Understanding the Maze Structure

### The 42 pattern

One of the project's visual requirements is to display the number **42** inside the maze.

The pattern is made of several fully closed cells, meaning that all four walls of each pattern cell remain closed.

These cells are excluded from the normal connectivity requirements.

If the maze dimensions are too small to accommodate the pattern, it is omitted and the application prints a message explaining why.

### Walls and directions

Each cell can have up to four walls:

| Direction | Meaning | Bit |
|---|---|---|
| North | Wall above the cell | 0 |
| East | Wall to the right | 1 |
| South | Wall below the cell | 2 |
| West | Wall to the left | 3 |

The project uses four bits to represent the wall configuration of each cell.

A bit set to `1` means the wall is closed.

A bit set to `0` means the wall is open.

### Hexadecimal wall encoding

Four binary bits represent one hexadecimal digit.

Each cell is therefore represented by a single hexadecimal character, from `0` to `F`.

| Hexadecimal | Binary | Closed walls |
|---|---|---|
| `0` | `0000` | None |
| `1` | `0001` | North |
| `2` | `0010` | East |
| `3` | `0011` | North, East |
| `4` | `0100` | South |
| `5` | `0101` | North, South |
| `6` | `0110` | East, South |
| `7` | `0111` | North, East, South |
| `8` | `1000` | West |
| `9` | `1001` | North, West |
| `A` | `1010` | East, West |
| `B` | `1011` | North, East, West |
| `C` | `1100` | South, West |
| `D` | `1101` | North, South, West |
| `E` | `1110` | East, South, West |
| `F` | `1111` | All four walls |

**Example:**

```text
Hexadecimal: A
Binary:      1010
Bits:        3 2 1 0
Directions:  W S E N
```

`A` means that the East and West walls are closed, while the North and South walls are open.

**Important:** adjacent cells must always agree about their shared wall.

For example, if the East wall of cell `(x,y)` is open, the West wall of cell `(x+1,y)` must also be open.

The same rule applies to all neighbouring cells.

This guarantees a coherent maze structure.

---

## Output File Format

The generated maze is saved to the path defined by `OUTPUT_FILE`.

The output file contains:

1. The maze grid, encoded using hexadecimal digits.
2. An empty line.
3. The entrance coordinates.
4. The exit coordinates.
5. The shortest path, represented using direction letters.

### Example

```text
F9A3C
8B6D2
F1E4A
C8B7F

0,0
4,2
EESSE
```

*The values above are illustrative and do not represent a guaranteed valid maze.*

### Output rules

- Each maze row must contain exactly `WIDTH` hexadecimal characters.
- The number of maze rows must equal `HEIGHT`.
- There must be an empty line after the maze grid.
- The next line contains the entrance coordinates.
- The following line contains the exit coordinates.
- The last line contains the shortest path.
- The path must use only `N`, `E`, `S` and `W`.
- All lines must end with a newline character (`\n`).

### Direction reference

| Letter | Movement |
|---|---|
| `N` | Move one cell up. |
| `E` | Move one cell right. |
| `S` | Move one cell down. |
| `W` | Move one cell left. |

For example, the path `EES` means:

```text
START
  |
  E
  v
  E
  v
  S
  v
DESTINATION
```

The path must correspond to valid openings in the generated maze and lead from the entrance to the exit.

---

## Reusable Module: mazegen

A major requirement of this project is code reusability.

The maze-generation logic must be independent of the main application, allowing it to be imported and reused in future Python projects.

For this purpose, the project provides a standalone package called **`mazegen`**.

### Package organization

The reusable generation logic is implemented in the `MazeGenerator` class, located in:

```text
mazegen/
    generator.py
```

The package is responsible for:

- Generating the maze.
- Managing its internal structure.
- Applying the selected generation algorithm.
- Handling the perfect and playable modes.
- Providing access to the generated cells.
- Calculating the shortest path.

The main application (`a_maze_ing.py`) handles the configuration file, terminal display, interactive menu and output-file formatting.

This separation makes the generator independent of the interface and file format.

### Installing the package

The project provides the built package at the root of the repository:

```text
mazegen-1.0.0-py3-none-any.whl
mazegen-1.0.0.tar.gz
```

Install the wheel using:

```bash
pip install mazegen-1.0.0-py3-none-any.whl
```

### Basic usage

```python
from mazegen import MazeGenerator

gen = MazeGenerator(
    width=20,
    height=15,
    entry=(0, 0),
    exit=(19, 14),
    perfect=True,
    seed=42
)

gen.generate()

print(gen.solve())
print(gen.solve_cells())
```

### Constructor parameters

| Parameter | Description |
|---|---|
| `width` | Number of maze columns. |
| `height` | Number of maze rows. |
| `entry` | Entrance coordinates `(x, y)`. |
| `exit` | Exit coordinates `(x, y)`. |
| `perfect` | Defines whether the maze is perfect. |
| `seed` | Random seed used for reproducibility. |
| `algorithm` | Generation algorithm: `dfs`, `prim` or `kruskal`. |

Invalid parameter values raise `ValueError`.

You can also generate another maze by passing a new seed:

```python
gen.generate(seed=123)
```

### Accessing the generated structure

The generator provides access to the following attributes and methods:

| Attribute / Method | Description |
|---|---|
| `gen.grid` | Internal maze structure. |
| `gen.pattern_cells` | Cells belonging to the 42 pattern. |
| `gen.dead_ends()` | Returns information about dead ends. |
| `gen.loop_count()` | Returns the number of loops. |
| `gen.solve()` | Returns the shortest path as direction letters. |
| `gen.solve_cells()` | Returns the shortest path as cell coordinates. |
| `gen.generate()` | Generates a new maze. |

### Understanding `gen.grid`

The internal grid is a two-dimensional structure accessed using:

```python
gen.grid[y][x]
```

Each cell contains an integer between `0` and `15`, representing its four walls.

For example:

```python
cell = gen.grid[0][0]
print(cell)
```

The value is the decimal representation of the four wall bits.

The internal representation is not necessarily the same as the final output file. The application converts the generated structure into the required hexadecimal format.

---

## Technical Notes & Validation

This section gathers useful commands, concepts and practical procedures for checking the application and understanding its main components.

### 1. Checking the generated maze

The project subject provides a Python analysis script called `maze_analyzer.py`.

This script verifies the maze's wall coherence and evaluates whether the generated maze meets the requirements of its selected mode.

Run it with:

```bash
python3 maze_analyzer.py maze.txt
```

The argument is the generated output file.

The analyzer checks:

- Whether neighbouring cells have coherent walls.
- Whether the maze is connected.
- Whether the maze is perfect.
- Whether the maze is suitable for Pac-Man-like gameplay.
- The number of loops.
- The number of dead ends.

### 2. Checking the two generation modes

To verify the perfect mode:

1. Open `config.txt`.
2. Set `PERFECT=True`.
3. Generate the maze.
4. Analyze the resulting file.

```bash
python3 a_maze_ing.py config.txt
python3 maze_analyzer.py maze.txt
```

The expected result is a perfect maze with a single path between any two cells and no loops.

To verify the playable mode:

1. Change `PERFECT=False`.
2. Generate another maze.
3. Analyze the resulting file.

```bash
python3 a_maze_ing.py config.txt
python3 maze_analyzer.py maze.txt
```

The expected result is a `Pac-Man-USABLE` maze, with multiple independent routes and the required connectivity.

### 3. Checking the no-dead-end bonus

The analyzer also supports a maximum dead-end parameter.

To check a fully braided playable maze:

```bash
python3 maze_analyzer.py maze.txt --max-dead-ends 0
```

The expected result is a `Pac-Man-USABLE` verdict with zero dead ends.

This is an additional bonus requirement, not a mandatory condition for the playable mode.

### 4. Checking reproducibility

A seed controls the random generation process.

Using the same configuration, algorithm and seed should reproduce the same maze.

Example:

```ini
WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
SEED=42
ALGORITHM=dfs
```

Run the application:

```bash
python3 a_maze_ing.py config.txt
```

Save or inspect the generated output, then run the application again without changing the configuration.

The generated maze should be identical.

To generate a different maze, change the seed:

```ini
SEED=123
```

### 5. Checking configuration errors

The application should handle invalid configurations gracefully.

Useful cases to understand and test include:

| Test | Modification | Expected behaviour |
|---|---|---|
| Missing mandatory key | Remove `WIDTH`. | Report the missing parameter. |
| Invalid syntax | Add a line without `=`. | Report a configuration syntax error. |
| Invalid integer | Set `WIDTH=abc`. | Report an invalid numeric value. |
| Invalid boolean | Set `PERFECT=maybe`. | Report an invalid boolean value. |
| Invalid coordinates | Set `ENTRY=0`. | Report an invalid coordinate format. |
| Out-of-bounds coordinates | Set `EXIT=200,14`. | Report coordinates outside the maze. |
| Same entrance and exit | Set `ENTRY=0,0` and `EXIT=0,0`. | Report invalid positions. |
| Duplicate key | Add a second `WIDTH`. | Report a duplicate parameter. |
| Unknown key | Add `UNKNOWN=value`. | Print a warning and ignore the key. |
| Missing configuration | Use a nonexistent file. | Report that the file cannot be found. |

Errors must be displayed clearly, using the format:

```text
Error: <explanation>
```

The program should write error messages to standard error and exit with status code `1`, without displaying an unexpected traceback.

### 6. Checking the output file

After generating a maze, inspect the output:

```bash
cat maze.txt
```

You can also count the number of lines:

```bash
wc -l maze.txt
```

Remember that the file must contain:

- `HEIGHT` maze rows.
- One empty line.
- The entrance.
- The exit.
- The shortest path.

The maze grid must have exactly `WIDTH` hexadecimal characters per row.

### 7. Checking code quality

Run:

```bash
make lint
```

The mandatory lint checks include:

```bash
flake8 .
```

And:

```bash
mypy . --warn-return-any --warn-unused-ignores \
--ignore-missing-imports --disallow-untyped-defs \
--check-untyped-defs
```

For stricter verification:

```bash
make lint-strict
```

This executes:

```bash
flake8 .
mypy . --strict
```

The project follows Python typing conventions, uses type hints and documents functions and classes with docstrings following PEP 257.

### 8. Running automated tests

The project includes automated tests using pytest.

Run:

```bash
make test
```

Or:

```bash
pytest
```

Tests help verify functionality, edge cases and expected behaviour without having to execute every operation manually.

### 9. Rebuilding the reusable package

The package must be reproducible from its source files.

Use the following commands:

```bash
make build
```

Alternatively, inside a virtual environment:

```bash
pip install build
python -m build
```

The standard build command generates the distribution files inside `dist/`:

```text
dist/
    mazegen-1.0.0.tar.gz
    mazegen-1.0.0-py3-none-any.whl
```

The project's Makefile also copies the resulting artifacts to the repository root.

### 10. Testing package installation independently

A useful way to verify reusability is to build the package in one environment and install it in another.

Create a new virtual environment:

```bash
python3 -m venv test_env
```

Activate it:

```bash
source test_env/bin/activate
```

Install the newly generated package:

```bash
pip install ./mazegen-1.0.0-py3-none-any.whl
```

Test the import:

```bash
python -c "from mazegen import MazeGenerator; print('mazegen installed successfully')"
```

You can then use the installed package in a separate Python script or application.

Deactivate the environment when finished:

```bash
deactivate
```

---

## Project Structure

The main components are organized around the separation between the reusable generator and the application.

```text
A-Maze-ing/
│
│
├── a_maze_ing.py
│
├── config.txt
│
├── app/  
│   ├── __init__.py
│   ├── config.py          
│   ├── output.py          
│   └── render.py
│
├── mazegen/               
│   ├── __init__.py        
│   ├── generator.py       
│   ├── pattern.py         
│   └── py.typed
│
├── pyproject.toml     
├── mazegen-1.0.0.tar.gz   
├── mazegen-1.0.0-py3-none-any.whl
├── Makefile
├── README.md
├── LICENSE.md             
├── .gitignore
└── tests/                 
```

*This diagram illustrates the main project components. Additional files and subdirectories may be present in the repository.*

### Main components

| Component | Responsibility |
|---|---|
| `a_maze_ing.py` | Main application entry point. |
| `mazegen/` | Reusable maze-generation package. |
| `mazegen/generator.py` | `MazeGenerator` implementation. |
| `app/` | Application-specific components. |
| `config.txt` | Default maze configuration. |
| `maze.txt` | Generated maze output. |
| `Makefile` | Automates development and execution commands. |
| `tests/` | Automated tests. |
| `docs/estudo.html` | Additional study documentation. |
| `LICENSE.md` | Defines the conditions for reusing and distributing the generator. |
| `README.md` | Project documentation. |
| `mazegen-*.whl` | Built Python wheel distribution. |
| `mazegen-*.tar.gz` | Source distribution. |

---

## Resources

The following references were used to understand the algorithms, Python concepts, packaging and project requirements.

### Maze generation and graph theory

- [Maze Generation Algorithms — Wikipedia](https://en.wikipedia.org/wiki/Maze_generation_algorithm): Overview of common maze-generation techniques, including DFS, Prim and Kruskal.
- [Mazes for Programmers — Jamis Buck](https://pragprog.com/titles/jbmaze/mazes-for-programmers/): Practical explanations of maze generation, spanning trees, braiding and dead ends.
- [Breadth-First Search — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search): Explanation of BFS and graph traversal.

### Python and code quality

- [Python Documentation](https://docs.python.org/3/): Official Python documentation.
- [Python Random Module](https://docs.python.org/3/library/random.html): Random number generation and seeds.
- [Python Collections](https://docs.python.org/3/library/collections.html): Data structures such as queues.
- [Python Dataclasses](https://docs.python.org/3/library/dataclasses.html): Data classes and structured objects.
- [Python Typing](https://docs.python.org/3/library/typing.html): Type hints and static typing.
- [PEP 8](https://peps.python.org/pep-0008/): Python coding style conventions.
- [PEP 257](https://peps.python.org/pep-0257/): Docstring conventions.
- [mypy](https://mypy.readthedocs.io/): Static type checking.
- [flake8](https://flake8.pycqa.org/): Python code style and quality checks.
- [pytest](https://docs.pytest.org/): Python testing framework.

### Packaging and terminal visualization

- [Python Packaging User Guide](https://packaging.python.org/): Building, distributing and installing Python packages.
- [Python Build](https://build.pypa.io/): Building Python source and wheel distributions.
- [ANSI Escape Codes](https://en.wikipedia.org/wiki/ANSI_escape_code): Terminal colours and text formatting.

### Project documentation

- `docs/estudo.html`: Additional study guide in Portuguese, explaining the concepts used throughout the project.

### Use of AI

AI tools were used as learning and documentation assistants, not as a substitute for understanding or developing the solution.

The tools used included **Claude Code** and **Gemini**.

Their use included:

- Helping organize and structure the `README.md`.
- Translating technical subjects and project requirements.
- Identifying relevant study materials and references.
- Supporting the preparation of documentation and explanations of the concepts involved in the project.

AI-generated suggestions and information were treated as material to review and verify. The project documentation was organized to support understanding, and the implementation was not generated by AI.

The use of AI followed the project's learning principles: critically evaluate generated content, test suggestions and only use material that can be understood and explained.

---

## Team and Project Management

### Team members and responsibilities

| Team member | Role |
|---|---|
| `alesferr` | Development, research, testing and documentation. |
| `edgda-si` | Development, research, testing and documentation. |

Both team members participated in all project phases and shared responsibility for the implementation.

### Planning and development

The project was divided into phases to make implementation and collaboration easier.

The initial plan included:

1. Project skeleton and development tools.
2. Configuration-file parser.
3. Maze-generation engine.
4. Implementation of the 42 pattern.
5. Playable mode and braiding logic.
6. Terminal visualization and interactive menu.
7. Reusable package and Python packaging.
8. README and additional documentation.
9. Bonus features.
10. Testing and preparation for the project defence.

The original sequence was followed successfully. Additional time was dedicated to the braiding logic, edge cases and testing the generation process, particularly to ensure that the implementation did not depend on Python's recursion-depth limit.

### What worked well

- Pair programming helped us understand and debug the generation algorithms.
- Dividing the project into phases made development more organized.
- Collaborative discussions helped us identify implementation problems.
- Testing different maze configurations helped us verify the behaviour of both generation modes.
- Working together made it easier to investigate unexpected results and improve the implementation.

### What could be improved

One improvement for future projects would be to design and write unit tests before implementing the main functionality.

This would help identify edge cases earlier, provide clearer implementation goals and reduce the amount of debugging required later.

### Tools used

| Tool | Purpose |
|---|---|
| Python 3 | Main programming language. |
| Git / GitHub | Version control and collaboration. |
| Make | Automation of development commands. |
| flake8 | Code style verification. |
| mypy | Static type checking. |
| pytest | Automated testing. |
| `build` | Python package generation. |
| Linux / Terminal | Development environment and command execution. |
| Claude Code | AI-assisted learning and documentation support. |
| Gemini | AI-assisted research, translation and study support. |

---

## License

This project uses the **MIT License**, documented in `LICENSE.md`.

The MIT License allows the maze generator to be reused, modified and distributed in future projects, provided that the license and copyright notice are retained.

This is particularly important because `mazegen` was designed to be independently reusable in subsequent projects.

---

**A-Maze-ing**
