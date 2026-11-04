"""Small command-line entry point for the first project workflow."""

import argparse
import sqlite3
from pathlib import Path

from .project import ProjectSettings, create_project, open_project

'''
.venv/bin/python -m sprite_motion_lab create "Cat Study" --width 48 --height 48
.venv/bin/python -m sprite_motion_lab show "project_data/cat-study-xxxxxxxx"
'''

# Read the input either from the call to main or from the arguments typed in terminal
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="sprite_motion_lab")

    # Telling argparse that the program supports multiple commands
    # dest='command' tells argparse to store the selected command in args.command
    commands = parser.add_subparsers(dest="command", required=True)

    # Creating a command called 'create'
    create = commands.add_parser("create", help="Create a local project")
    # Defining the inputs that the command accepts
    create.add_argument("name", help="Project name") # Positional arguments without "--" are required by default
    create.add_argument("--width", type=int, default=64, help="Canvas width in pixels")
    create.add_argument("--height", type=int, default=64, help="Canvas height in pixels")
    create.add_argument("--root", type=Path, default=Path("project_data"), help='Project root path')

    # Creating a command called 'show'
    show = commands.add_parser("show", help="Show a saved project's settings")
    # Defining the inputs that the command accepts
    show.add_argument("path", type=Path, help="Path printed by the create command")

    args = parser.parse_args(argv)
    try:
        if args.command == "create":
            settings = ProjectSettings(args.name, args.width, args.height)
            project = create_project(settings, args.root)
            print("Created project")
        else:
            project = open_project(args.path)
            print("Opened project")
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.error(str(error))

    print(f"Name: {project.settings.name}")
    print(f"Canvas: {project.settings.canvas_width} x {project.settings.canvas_height}")
    print(f"Path: {project.path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
