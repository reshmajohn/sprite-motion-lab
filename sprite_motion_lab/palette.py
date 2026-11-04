"""Deterministic candidate-palette extraction from a canonical sprite."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

from .project import open_project
from .sprites import get_canonical_sprite


@dataclass(frozen=True)
class PaletteColor:
    red: int
    green: int
    blue: int
    alpha: int
    pixel_count: int

    @property
    def hex_rgba(self) -> str:
        """Return all four channels in an unambiguous display format."""
        return f"#{self.red:02X}{self.green:02X}{self.blue:02X}{self.alpha:02X}"


@dataclass(frozen=True)
class ExtractedPalette:
    colors: tuple[PaletteColor, ...]
    transparent_pixel_count: int
    total_pixel_count: int


def extract_canonical_palette(project_path: Path) -> ExtractedPalette:
    """Count exact visible RGBA colors in a project's canonical sprite."""
    project = open_project(project_path)
    sprite = get_canonical_sprite(project.path)
    if sprite is None:
        raise ValueError("This child project does not have a canonical sprite.")

    with Image.open(project.path / sprite.relative_path) as image:
        rgba_image = image.convert("RGBA")
        counts = Counter(rgba_image.get_flattened_data())

    transparent_pixel_count = sum(
        count for (*_, alpha), count in counts.items() if alpha == 0
    )
    visible_counts = [
        (rgba, count) for rgba, count in counts.items() if rgba[3] != 0
    ]
    visible_counts.sort(key=lambda item: (-item[1], item[0]))
    colors = tuple(
        PaletteColor(*rgba, pixel_count=count) for rgba, count in visible_counts
    )
    return ExtractedPalette(colors, transparent_pixel_count, rgba_image.width * rgba_image.height)
