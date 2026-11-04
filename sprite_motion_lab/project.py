"""Create and reopen local Sprite Motion Lab projects."""

import re
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


DATABASE_NAME = "project.sqlite3"
SCHEMA_VERSION = 2


def _create_canonical_sprite_table(connection: sqlite3.Connection) -> None:
    connection.execute(
        """CREATE TABLE IF NOT EXISTS canonical_sprite (
            id TEXT PRIMARY KEY,
            source_name TEXT NOT NULL,
            relative_path TEXT NOT NULL,
            sha256 TEXT NOT NULL,
            width INTEGER NOT NULL,
            height INTEGER NOT NULL,
            imported_at TEXT NOT NULL
        )"""
    )


def _upgrade_project_schema(connection: sqlite3.Connection) -> None:
    """Add sprite storage to a project created before imports existed."""
    version = connection.execute("PRAGMA user_version").fetchone()[0]
    if version == 1:
        _create_canonical_sprite_table(connection)
        connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")
    elif version != SCHEMA_VERSION:
        raise ValueError(f"Unsupported project schema version: {version}")


@dataclass(frozen=True)
class ProjectSettings:
    name: str
    canvas_width: int = 64
    canvas_height: int = 64

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("Project name must not be empty.")
        object.__setattr__(self, "name", self.name.strip())

        for label, value in (
            ("Canvas width", self.canvas_width),
            ("Canvas height", self.canvas_height),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                raise ValueError(f"{label} must be a positive whole number.")


@dataclass(frozen=True)
class Project:
    id: str
    settings: ProjectSettings
    path: Path
    created_at: str


def _save_project(
    settings: ProjectSettings, project_path: Path, project_id: str | None = None
) -> Project:
    project_id = project_id or uuid4().hex
    created_at = datetime.now(timezone.utc).isoformat()
    with closing(sqlite3.connect(project_path / DATABASE_NAME)) as connection:
        with connection:
            connection.execute(
                """CREATE TABLE project (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    canvas_width INTEGER NOT NULL,
                    canvas_height INTEGER NOT NULL,
                    created_at TEXT NOT NULL
                )"""
            )
            connection.execute(
                """INSERT INTO project
                   (id, name, canvas_width, canvas_height, created_at)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    project_id,
                    settings.name,
                    settings.canvas_width,
                    settings.canvas_height,
                    created_at,
                ),
            )
            _create_canonical_sprite_table(connection)
            connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    return Project(project_id, settings, project_path, created_at)


def create_project(
    settings: ProjectSettings, projects_root: Path = Path("project_data")
) -> Project:
    """Create a new project directory and save its settings in SQLite."""
    project_id = uuid4().hex
    slug = re.sub(r"[^a-z0-9]+", "-", settings.name.lower()).strip("-")
    slug = slug[:48].rstrip("-") or "project"
    project_path = Path(projects_root) / f"{slug}-{project_id[:8]}"
    project_path.mkdir(parents=True, exist_ok=False)
    return _save_project(settings, project_path, project_id)


def initialize_project_directory(settings: ProjectSettings, project_path: Path) -> Project:
    """Add project metadata to an existing folder without replacing its files."""
    project_path = Path(project_path)
    if not project_path.exists():
        raise FileNotFoundError(f"Child project folder does not exist: {project_path}")
    if not project_path.is_dir():
        raise NotADirectoryError(f"Child project path is not a folder: {project_path}")
    if (project_path / DATABASE_NAME).exists():
        raise FileExistsError(f"Project metadata already exists in {project_path}")
    return _save_project(settings, project_path)


def open_project(project_path: Path) -> Project:
    """Read a previously created project's saved settings."""
    project_path = Path(project_path)
    database_path = project_path / DATABASE_NAME
    if not database_path.is_file():
        raise FileNotFoundError(f"No project database found at {database_path}")

    with closing(sqlite3.connect(database_path)) as connection:
        version = connection.execute("PRAGMA user_version").fetchone()[0]
        if version not in (1, SCHEMA_VERSION):
            raise ValueError(f"Unsupported project schema version: {version}")
        row = connection.execute(
            "SELECT id, name, canvas_width, canvas_height, created_at FROM project"
        ).fetchone()

    if row is None:
        raise ValueError(f"Project settings are missing from {database_path}")
    project_id, name, width, height, created_at = row
    settings = ProjectSettings(name, width, height)
    return Project(project_id, settings, project_path, created_at)
