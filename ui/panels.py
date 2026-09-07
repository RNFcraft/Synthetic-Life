from typing import Iterable


def draw_lines(surface: object, font: object, lines: Iterable[str], x: int, y: int, color: tuple[int, int, int], spacing: int = 24) -> None:
    for index, line in enumerate(lines):
        rendered = font.render(line, True, color)  # type: ignore[attr-defined]
        surface.blit(rendered, (x, y + index * spacing))  # type: ignore[attr-defined]

