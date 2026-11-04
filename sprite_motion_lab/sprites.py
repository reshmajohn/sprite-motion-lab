"""Non-destructive import of a canonical PNG sprite."""

import hashlib
import sqlite3
import struct
import zlib
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from .project import (
    DATABASE_NAME,
    _upgrade_project_schema,
    open_project,
)


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


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
    """Check the PNG signature and IHDR chunk, then read its dimensions."""
    with path.open("rb") as image:
        header = image.read(33)

    if (
        len(header) != 33
        or header[:8] != PNG_SIGNATURE
        or int.from_bytes(header[8:12], "big") != 13
        or header[12:16] != b"IHDR"
        or zlib.crc32(header[12:29]) != int.from_bytes(header[29:33], "big")
    ):
        raise ValueError("The source does not have a valid PNG header.")

    width, height = struct.unpack(">II", header[16:24])
    if width == 0 or height == 0:
        raise ValueError("PNG dimensions must be positive.")
    return width, height


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
