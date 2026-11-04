"""Offline checks for deterministic canonical-sprite palette extraction."""

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from PIL import Image

from sprite_motion_lab.__main__ import main
from sprite_motion_lab.palette import PaletteColor, extract_canonical_palette
from sprite_motion_lab.project import ProjectSettings, create_project
from sprite_motion_lab.sprites import import_canonical_sprite


def _save_rgba_png(path: Path) -> None:
    with Image.new("RGBA", (2, 2)) as image:
        image.putdata(
            [
                (0, 0, 0, 0),
                (255, 0, 0, 255),
                (0, 0, 255, 128),
                (255, 0, 0, 255),
            ]
        )
        image.save(path, format="PNG")


class PaletteTests(unittest.TestCase):
    def test_extracts_visible_rgba_colors_with_deterministic_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            project = create_project(ProjectSettings("Cat Study"), root)
            source = root / "cat.png"
            _save_rgba_png(source)
            import_canonical_sprite(project.path, source)

            palette = extract_canonical_palette(project.path)

            self.assertEqual(
                palette.colors,
                (
                    PaletteColor(255, 0, 0, 255, 2),
                    PaletteColor(0, 0, 255, 128, 1),
                ),
            )
            self.assertEqual(palette.transparent_pixel_count, 1)
            self.assertEqual(palette.total_pixel_count, 4)

    def test_show_palette_command_displays_counts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)
            child = create_project(ProjectSettings("Pouncing Cat"), parent.path)
            source = root / "cat.png"
            _save_rgba_png(source)
            import_canonical_sprite(child.path, source)

            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["show-palette", str(child.path)]), 0)

            self.assertIn("Candidate palette: 2 nontransparent colors", output.getvalue())
            self.assertIn("#FF0000FF: 2 pixels", output.getvalue())
            self.assertIn("#0000FF80: 1 pixel", output.getvalue())
            self.assertIn("Fully transparent pixels: 1", output.getvalue())

    def test_show_palette_requires_canonical_sprite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)
            child = create_project(ProjectSettings("Pouncing Cat"), parent.path)

            error_output = io.StringIO()
            with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_result:
                main(["show-palette", str(child.path)])

            self.assertEqual(exit_result.exception.code, 2)
            self.assertIn("does not have a canonical sprite", error_output.getvalue())


if __name__ == "__main__":
    unittest.main()
