"""Small command-line entry point for the first project workflow."""

import argparse
import sqlite3
from pathlib import Path

from .project import (
    DATABASE_NAME,
    Project,
    ProjectSettings,
    create_project,
    initialize_project_directory,
    open_project,
)
from .sprites import get_canonical_sprite, import_canonical_sprite

'''
.venv/bin/python -m sprite_motion_lab create "Cat Animations"
# Choose one project setup command:
.venv/bin/python -m sprite_motion_lab add-project "PARENT_DIR_FROM_CREATE" "Pouncing Cat"
.venv/bin/python -m sprite_motion_lab import-project "EXISTING_CHILD_DIR"
# Then import the sprite:
.venv/bin/python -m sprite_motion_lab import-sprite "CHILD_DIR" "/path/to/cat.png"
'''


def _open_parent(directory: Path) -> Project:
    try:
        parent = open_project(directory)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            f"No initialized parent directory at {directory}. Run create first."
        ) from error

    if (directory.resolve().parent / DATABASE_NAME).is_file():
        raise ValueError(
            f"{directory} is an initialized child project, not a parent directory."
        )
    return parent


# Read the input either from the call to main or from the arguments typed in terminal
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="sprite_motion_lab",
        description="Create a parent directory, then add or use a child sprite project.",
    )

    # Telling argparse that the program supports multiple commands
    # dest='command' tells argparse to store the selected command in args.command
    commands = parser.add_subparsers(dest="command", required=True)

    # Creating a command called 'create'
    create = commands.add_parser(
        "create",
        help="Create a parent directory with default canvas dimensions",
        description="Creates a parent directory for related sprite projects and saves default canvas dimensions for its children.",
    )
    # Defining the inputs that the command accepts
    create.add_argument("name", help="Name for the new parent directory") # Positional arguments without "--" are required by default
    create.add_argument("--width", type=int, default=64, help="Default child canvas width in pixels")
    create.add_argument("--height", type=int, default=64, help="Default child canvas height in pixels")
    create.add_argument(
        "--storage-dir",
        type=Path,
        default=Path("project_data"),
        metavar="DIRECTORY",
        help="Where to place new parent directories (default: project_data)",
    )

    # Creating a command called 'show'
    show = commands.add_parser("show", help="Show a parent or child directory's saved settings")
    # Defining the inputs that the command accepts
    show.add_argument(
        "directory", type=Path, metavar="DIRECTORY", help="Path printed by create, add-project, or import-project"
    )

    add_project = commands.add_parser(
        "add-project",
        help="Create a child project with canvas settings",
        description="Creates a named child project inside PARENT_DIR. Canvas dimensions inherit the parent's defaults unless overridden. Import its sprite separately.",
    )
    add_project.add_argument(
        "parent_directory", type=Path, metavar="PARENT_DIR", help="Parent directory printed by create"
    )
    add_project.add_argument(
        "project_name", metavar="PROJECT_NAME", help="Name for the new child project"
    )
    add_project.add_argument("--width", type=int, help="Child canvas width; defaults to parent's width")
    add_project.add_argument("--height", type=int, help="Child canvas height; defaults to parent's height")

    import_project = commands.add_parser(
        "import-project",
        help="Initialize a child folder you already made",
        description="Adds project settings to an existing child folder inside an initialized parent. Keeps the folder's other files.",
    )
    import_project.add_argument(
        "project_directory", type=Path, metavar="CHILD_DIR", help="Existing child folder to use"
    )
    import_project.add_argument("--width", type=int, help="Child canvas width; defaults to parent's width")
    import_project.add_argument("--height", type=int, help="Child canvas height; defaults to parent's height")

    import_sprite = commands.add_parser(
        "import-sprite",
        help="Copy a PNG into an initialized child project",
        description="Copies PNG_FILE into CHILD_DIR after add-project or import-project, without changing saved canvas settings.",
    )
    import_sprite.add_argument(
        "project_directory", type=Path, metavar="CHILD_DIR", help="Child project path from add-project or import-project"
    )
    import_sprite.add_argument("png_file", type=Path, metavar="PNG_FILE", help="Original PNG to copy")

    args = parser.parse_args(argv)
    try:
        if args.command == "add-project":
            parent = _open_parent(args.parent_directory)
            width = args.width if args.width is not None else parent.settings.canvas_width
            height = args.height if args.height is not None else parent.settings.canvas_height
            child_settings = ProjectSettings(args.project_name, width, height)
            child = create_project(child_settings, parent.path)
            print("Created child project")
            print(f"Name: {child.settings.name}")
            print(f"Canvas: {child.settings.canvas_width} x {child.settings.canvas_height}")
            print(f"Child project directory: {child.path}")
            return 0

        if args.command == "import-project":
            child_directory = args.project_directory
            if not child_directory.is_dir():
                raise FileNotFoundError(
                    f"Existing child folder not found: {child_directory}. "
                    "Create it yourself or use add-project."
                )
            parent = _open_parent(child_directory.parent)
            if child_directory.resolve().parent != parent.path.resolve():
                raise ValueError("The child folder must be directly inside its parent directory.")
            try:
                child = open_project(child_directory)
            except FileNotFoundError:
                width = args.width if args.width is not None else parent.settings.canvas_width
                height = args.height if args.height is not None else parent.settings.canvas_height
                settings = ProjectSettings(child_directory.name, width, height)
                child = initialize_project_directory(settings, child_directory)
                print("Initialized existing child folder")
            else:
                if args.width is not None or args.height is not None:
                    raise ValueError("This child already has canvas settings; omit --width and --height.")
                print("Child project already initialized")
            print(f"Name: {child.settings.name}")
            print(f"Canvas: {child.settings.canvas_width} x {child.settings.canvas_height}")
            print(f"Child project directory: {child.path}")
            return 0

        if args.command == "import-sprite":
            child_directory = args.project_directory
            if not child_directory.is_dir():
                raise FileNotFoundError(f"Child project folder not found: {child_directory}")
            parent = _open_parent(child_directory.parent)
            if child_directory.resolve().parent != parent.path.resolve():
                raise ValueError("The child folder must be directly inside its parent directory.")
            try:
                child = open_project(child_directory)
            except FileNotFoundError as error:
                raise FileNotFoundError(
                    f"Child project is not initialized at {child_directory}. "
                    "Run import-project first."
                ) from error
            sprite = import_canonical_sprite(child.path, args.png_file)
            print("Imported canonical sprite")
            print(f"Child project directory: {child.path}")
            print(f"PNG dimensions: {sprite.width} x {sprite.height}")
            print(f"SHA-256: {sprite.sha256}")
            print(f"Saved copy: {child.path / sprite.relative_path}")
            return 0

        if args.command == "create":
            settings = ProjectSettings(args.name, args.width, args.height)
            project = create_project(settings, args.storage_dir)
            print("Created parent directory")
        else:
            project = open_project(args.directory)
            print("Opened directory")

        print(f"Name: {project.settings.name}")
        print(f"Canvas setting: {project.settings.canvas_width} x {project.settings.canvas_height}")
        print(f"Directory: {project.path}")
        if args.command == "show":
            sprite = get_canonical_sprite(project.path)
            if sprite is not None:
                print(f"Canonical sprite: {sprite.source_name} ({sprite.width} x {sprite.height})")
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
