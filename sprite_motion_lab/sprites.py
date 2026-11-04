"""Non-destructive import of a canonical PNG sprite."""

import hashlib
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from PIL import Image, UnidentifiedImageError

from .project import (
    DATABASE_NAME,
    _upgrade_project_schema,
    open_project,
)


@dataclass(frozen=True)
class CanonicalSprite:
    id: str
    source_name: str
    relative_path: Path
    sha256: str
    width: int
    height: int
    imported_at: str


def _read_png_dimensions(path: Path) -> tuple[int, int]:
    """Fully decode a PNG before returning its dimensions."""
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError("The source file must contain PNG image data.")
            image.verify()

        with Image.open(path) as image:
            image.load()
            return image.size
    except (UnidentifiedImageError, OSError, SyntaxError) as error:
        raise ValueError("The source is not a complete, readable PNG image.") from error


def import_canonical_sprite(project_path: Path, source_path: Path) -> CanonicalSprite:
    """Keep the source intact and save a hashed copy inside the project."""
    project = open_project(project_path)
    source = Path(source_path)
    if source.suffix.lower() != ".png":
        raise ValueError("The canonical sprite must be a .png file.")
    if not source.is_file():
        raise FileNotFoundError(f"Sprite file not found: {source}")
    width, height = _read_png_dimensions(source)

    sprite_id = uuid4().hex
    relative_path = Path("assets") / f"canonical-{sprite_id}.png"
    destination = project.path / relative_path
    imported_at = datetime.now(timezone.utc).isoformat()
    digest = hashlib.sha256()
    copied = False

    try:
        with closing(sqlite3.connect(project.path / DATABASE_NAME)) as connection:
            with connection:
                connection.execute("BEGIN IMMEDIATE")
                _upgrade_project_schema(connection)
                if connection.execute("SELECT 1 FROM canonical_sprite LIMIT 1").fetchone():
                    raise ValueError("This project already has a canonical sprite.")

                destination.parent.mkdir(exist_ok=True)
                with source.open("rb") as original, destination.open("xb") as saved:
                    copied = True
                    while block := original.read(1024 * 1024):
                        digest.update(block)
                        saved.write(block)

                if _read_png_dimensions(destination) != (width, height):
                    raise ValueError("The source changed while it was being imported.")
                connection.execute(
                    """INSERT INTO canonical_sprite
                       (id, source_name, relative_path, sha256, width, height, imported_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        sprite_id,
                        source.name,
                        relative_path.as_posix(),
                        digest.hexdigest(),
                        width,
                        height,
                        imported_at,
                    ),
                )
    except Exception:
        if copied:
            destination.unlink(missing_ok=True)
        raise

    return CanonicalSprite(
        sprite_id, source.name, relative_path, digest.hexdigest(), width, height, imported_at
    )


def get_canonical_sprite(project_path: Path) -> CanonicalSprite | None:
    """Return the saved canonical sprite metadata, if one was imported."""
    project = open_project(project_path)
    with closing(sqlite3.connect(project.path / DATABASE_NAME)) as connection:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version == 1:
            return None
        row = connection.execute(
            """SELECT id, source_name, relative_path, sha256, width, height, imported_at
               FROM canonical_sprite LIMIT 1"""
        ).fetchone()

    if row is None:
        return None
    sprite_id, source_name, relative_path, sha256, width, height, imported_at = row
    return CanonicalSprite(
        sprite_id, source_name, Path(relative_path), sha256, width, height, imported_at
    )
