from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GridLayout:
    left: int
    top: int
    cell: int
    width: int
    height: int


def fit_grid(area: tuple[int, int, int, int], columns: int, rows: int, padding: int = 24) -> GridLayout:
    x, y, width, height = area
    cell = max(1, min((width - padding * 2) // columns, (height - padding * 2) // rows))
    grid_width, grid_height = cell * columns, cell * rows
    return GridLayout(x + (width-grid_width)//2, y + (height-grid_height)//2, cell, grid_width, grid_height)

