"""Reusable maze generator package."""

from .generator import (
    ALGORITHMS,
    EAST,
    NORTH,
    SOUTH,
    WEST,
    MazeGenerator,
)
from .pattern import pattern_cells

__version__ = "1.0.0"

__all__ = [
    "ALGORITHMS",
    "EAST",
    "NORTH",
    "SOUTH",
    "WEST",
    "MazeGenerator",
    "pattern_cells",
]
