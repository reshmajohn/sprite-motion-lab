"""Offline import checks using a tiny PNG made in the test."""

import hashlib
import io
import sqlite3
import struct
import tempfile
import unittest
import zlib
from contextlib import closing, redirect_stderr, redirect_stdout
from pathlib import Path

from sprite_motion_lab.__main__ import main
from sprite_motion_lab.project import (
    DATABASE_NAME,
    SCHEMA_VERSION,
    ProjectSettings,
    create_project,
    initialize_project_directory,
    open_project,
)
from sprite_motion_lab.sprites import get_canonical_sprite, import_canonical_sprite


def _chunk(kind: bytes, payload: bytes) -> bytes:
    body = kind + payload
    return struct.pack(">I", len(payload)) + body + struct.pack(">I", zlib.crc32(body))


def _png_bytes(width: int = 2, height: int = 1) -> bytes:
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    pixels = b"\x00\x00\x00\x00" + b"\xff\x00\x00\xff" * (width - 1)
    rows = (b"\x00" + pixels) * height
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", zlib.compress(rows))
        + _chunk(b"IEND", b"")
    )


class CanonicalSpriteTests(unittest.TestCase):
    def test_import_preserves_source_and_reopens_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            project = create_project(ProjectSettings("Cat Study"), root)
            source = root / "cat.png"
            original = _png_bytes(2, 3)
            source.write_bytes(original)

            sprite = import_canonical_sprite(project.path, source)

            self.assertEqual(source.read_bytes(), original)
            self.assertEqual((project.path / sprite.relative_path).read_bytes(), original)
            self.assertEqual(sprite.sha256, hashlib.sha256(original).hexdigest())
            self.assertEqual((sprite.width, sprite.height), (2, 3))
            self.assertEqual(get_canonical_sprite(project.path), sprite)
            self.assertEqual(open_project(project.path), project)

    def test_rejects_invalid_png_before_copying(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            project = create_project(ProjectSettings("Cat Study"), root)
            source = root / "bad.png"
            source.write_bytes(b"not a PNG")

            with self.assertRaisesRegex(ValueError, "valid PNG header"):
                import_canonical_sprite(project.path, source)

            self.assertIsNone(get_canonical_sprite(project.path))
            self.assertFalse((project.path / "assets").exists())

    def test_second_import_keeps_first_copy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            project = create_project(ProjectSettings("Cat Study"), root)
            first_source = root / "first.png"
            first_source.write_bytes(_png_bytes())
            first = import_canonical_sprite(project.path, first_source)

            second_source = root / "second.png"
            second_source.write_bytes(_png_bytes(3, 1))
            with self.assertRaisesRegex(ValueError, "already has a canonical sprite"):
                import_canonical_sprite(project.path, second_source)

            self.assertEqual(get_canonical_sprite(project.path), first)
            self.assertEqual((project.path / first.relative_path).read_bytes(), first_source.read_bytes())

    def test_previous_schema_can_open_and_upgrade_on_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            project = create_project(ProjectSettings("Cat Study"), root)
            database = project.path / DATABASE_NAME
            with closing(sqlite3.connect(database)) as connection:
                with connection:
                    connection.execute("DROP TABLE canonical_sprite")
                    connection.execute("PRAGMA user_version = 1")

            self.assertEqual(open_project(project.path), project)
            self.assertIsNone(get_canonical_sprite(project.path))
            source = root / "cat.png"
            source.write_bytes(_png_bytes())
            sprite = import_canonical_sprite(project.path, source)

            self.assertEqual(get_canonical_sprite(project.path), sprite)
            with closing(sqlite3.connect(database)) as connection:
                self.assertEqual(connection.execute("PRAGMA user_version").fetchone()[0], SCHEMA_VERSION)

    def test_add_project_creates_child_without_sprite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)

            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["add-project", str(parent.path), "Cat Study"]), 0)
            self.assertIn("Created child project", output.getvalue())

            child_directories = [path for path in parent.path.iterdir() if path.is_dir()]
            self.assertEqual(len(child_directories), 1)
            child = child_directories[0]
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(main(["show", str(child)]), 0)
            self.assertIn("Canvas setting: 64 x 64", output.getvalue())
            self.assertIsNone(get_canonical_sprite(child))
            self.assertIsNone(get_canonical_sprite(parent.path))

    def test_children_can_have_different_canvas_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations", 64, 64), root)

            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["add-project", str(parent.path), "First Cat"]), 0)
                self.assertEqual(
                    main([
                        "add-project", str(parent.path), "Second Cat",
                        "--width", "32", "--height", "48",
                    ]),
                    0,
                )

            children = sorted(path for path in parent.path.iterdir() if path.is_dir())
            self.assertEqual(len(children), 2)
            settings_by_name = {open_project(path).settings.name: open_project(path).settings for path in children}
            self.assertEqual((settings_by_name["First Cat"].canvas_width, settings_by_name["First Cat"].canvas_height), (64, 64))
            self.assertEqual((settings_by_name["Second Cat"].canvas_width, settings_by_name["Second Cat"].canvas_height), (32, 48))
            self.assertTrue(all(get_canonical_sprite(path) is None for path in children))

    def test_bad_png_does_not_change_initialized_child(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)
            child = create_project(ProjectSettings("Cat Study"), parent.path)
            source = root / "bad.png"
            source.write_bytes(b"not a PNG")

            error_output = io.StringIO()
            with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_result:
                main(["import-sprite", str(child.path), str(source)])

            self.assertEqual(exit_result.exception.code, 2)
            self.assertIn("valid PNG header", error_output.getvalue())
            self.assertIsNone(get_canonical_sprite(child.path))
            self.assertFalse((child.path / "assets").exists())

    def test_missing_parent_import_explains_error(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            missing = Path(temporary_root) / "missing-project"
            error_output = io.StringIO()
            with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_result:
                main(["add-project", str(missing), "Cat Study"])

            self.assertEqual(exit_result.exception.code, 2)
            self.assertIn("No initialized parent directory", error_output.getvalue())
            self.assertIn("Run create first", error_output.getvalue())
            self.assertFalse(missing.exists())

    def test_add_project_rejects_child_as_parent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)
            child = create_project(ProjectSettings("Pouncing Cat"), parent.path)

            error_output = io.StringIO()
            with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_result:
                main(["add-project", str(child.path), "Grandchild"])

            self.assertEqual(exit_result.exception.code, 2)
            self.assertIn("initialized child project, not a parent", error_output.getvalue())
            self.assertFalse(any(path.is_dir() for path in child.path.iterdir()))

    def test_add_project_help_names_its_inputs(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as exit_result:
            main(["add-project", "--help"])

        self.assertEqual(exit_result.exception.code, 0)
        self.assertIn("PARENT_DIR", output.getvalue())
        self.assertIn("PROJECT_NAME", output.getvalue())
        self.assertNotIn("PNG_FILE", output.getvalue())
        self.assertIn("Child canvas width", output.getvalue())

    def test_import_project_then_sprite_preserves_manual_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations", 64, 64), root)
            child_folder = parent.path / "Pouncing Cat"
            child_folder.mkdir()
            notes = child_folder / "notes.txt"
            notes.write_text("Keep this note", encoding="utf-8")
            source = root / "cat.png"
            original = _png_bytes(3, 2)
            source.write_bytes(original)

            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    main(["import-project", str(child_folder), "--width", "32", "--height", "48"]),
                    0,
                )

            child = open_project(child_folder)
            self.assertIsNone(get_canonical_sprite(child_folder))
            self.assertIn("Initialized existing child folder", output.getvalue())
            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["import-sprite", str(child_folder), str(source)]), 0)

            sprite = get_canonical_sprite(child_folder)
            self.assertEqual(child.settings.name, "Pouncing Cat")
            self.assertEqual((child.settings.canvas_width, child.settings.canvas_height), (32, 48))
            self.assertEqual(source.read_bytes(), original)
            self.assertEqual((child_folder / sprite.relative_path).read_bytes(), original)
            self.assertEqual(notes.read_text(encoding="utf-8"), "Keep this note")
            self.assertIn(f"Child project directory: {child_folder}", output.getvalue())

    def test_import_project_reuses_initialized_child_settings(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)
            child_folder = parent.path / "Pouncing Cat"
            child_folder.mkdir()
            child = initialize_project_directory(ProjectSettings("Pouncing Cat", 48, 48), child_folder)

            with redirect_stdout(io.StringIO()):
                self.assertEqual(main(["import-project", str(child_folder)]), 0)

            self.assertEqual(open_project(child_folder), child)
            self.assertIsNone(get_canonical_sprite(child_folder))

    def test_import_project_folder_must_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)
            missing = parent.path / "Missing Cat"

            error_output = io.StringIO()
            with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_result:
                main(["import-project", str(missing)])

            self.assertEqual(exit_result.exception.code, 2)
            self.assertIn("Create it yourself or use add-project", error_output.getvalue())
            self.assertFalse(missing.exists())

    def test_import_project_help_names_child_path(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as exit_result:
            main(["import-project", "--help"])

        self.assertEqual(exit_result.exception.code, 0)
        self.assertIn("CHILD_DIR", output.getvalue())
        self.assertIn("existing child folder", output.getvalue())
        self.assertNotIn("PNG_FILE", output.getvalue())

    def test_import_sprite_requires_initialized_child(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_root:
            root = Path(temporary_root)
            parent = create_project(ProjectSettings("Cat Animations"), root)
            child_folder = parent.path / "Pouncing Cat"
            child_folder.mkdir()
            source = root / "cat.png"
            source.write_bytes(_png_bytes())

            error_output = io.StringIO()
            with redirect_stderr(error_output), self.assertRaises(SystemExit) as exit_result:
                main(["import-sprite", str(child_folder), str(source)])

            self.assertEqual(exit_result.exception.code, 2)
            self.assertIn("Run import-project first", error_output.getvalue())
            self.assertIsNone(get_canonical_sprite(parent.path))

    def test_import_sprite_help_uses_saved_child_settings(self) -> None:
        output = io.StringIO()
        with redirect_stdout(output), self.assertRaises(SystemExit) as exit_result:
            main(["import-sprite", "--help"])

        self.assertEqual(exit_result.exception.code, 0)
        self.assertIn("CHILD_DIR", output.getvalue())
        self.assertIn("PNG_FILE", output.getvalue())
        self.assertNotIn("--width", output.getvalue())


if __name__ == "__main__":
    unittest.main()
