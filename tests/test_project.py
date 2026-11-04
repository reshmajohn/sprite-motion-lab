"""Offline checks for local project creation and reopening."""

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from sprite_motion_lab.__main__ import main
from sprite_motion_lab.project import (
    DATABASE_NAME,
    ProjectSettings,
    create_project,
    initialize_project_directory,
    open_project,
)


class ProjectTests(unittest.TestCase):
    def test_create_and_reopen_custom_canvas(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            settings = ProjectSettings("  Cat Study  ", 48, 32)
            created = create_project(settings, Path(temporary_root))

            self.assertTrue((created.path / DATABASE_NAME).is_file())
            self.assertEqual(created.settings.name, "Cat Study")
            self.assertEqual(open_project(created.path), created)

    def test_same_name_creates_distinct_projects(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            first = create_project(ProjectSettings("Cat Study"), root)
            second = create_project(ProjectSettings("Cat Study"), root)

            self.assertNotEqual(first.id, second.id)
            self.assertNotEqual(first.path, second.path)
            self.assertEqual(open_project(first.path), first)

    def test_invalid_settings_are_rejected(self) -> None:
        for settings in (
            ("   ", 64, 64),
            ("Cat", 0, 64),
            ("Cat", 64, True),
        ):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                ProjectSettings(*settings)

    def test_open_missing_project_does_not_create_it(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            missing = Path(temporary_root) / "missing"
            with self.assertRaisesRegex(FileNotFoundError, "No project database"):
                open_project(missing)
            self.assertFalse(missing.exists())

    def test_initialize_existing_folder_preserves_its_files(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            folder = Path(temporary_root) / "Pouncing Cat"
            folder.mkdir()
            notes = folder / "notes.txt"
            notes.write_text("Keep this file", encoding="utf-8")

            project = initialize_project_directory(ProjectSettings("Pouncing Cat", 48, 48), folder)

            self.assertEqual(open_project(folder), project)
            self.assertEqual(notes.read_text(encoding="utf-8"), "Keep this file")
            with self.assertRaises(FileExistsError):
                initialize_project_directory(ProjectSettings("Pouncing Cat"), folder)

    def test_initialize_requires_existing_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            missing = Path(temporary_root) / "missing"
            with self.assertRaises(FileNotFoundError):
                initialize_project_directory(ProjectSettings("Missing"), missing)
            self.assertFalse(missing.exists())

    def test_command_line_create_and_show(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["create", "Cat Study", "--storage-dir", temporary_root]), 0)
            self.assertIn("Created parent directory", output.getvalue())

            project_path = next(Path(temporary_root).iterdir())
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["show", str(project_path)]), 0)
            self.assertIn("Canvas setting: 64 x 64", output.getvalue())

    def test_create_help_describes_parent_directory_and_defaults(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as exit_result:
            main(["create", "--help"])

        self.assertEqual(exit_result.exception.code, 0)
        self.assertIn("--storage-dir DIRECTORY", output.getvalue())
        self.assertIn("Where to place new parent directories", output.getvalue())
        self.assertIn("Default child canvas width", output.getvalue())
        self.assertNotIn("--sprite", output.getvalue())


if __name__ == "__main__":
    unittest.main()
