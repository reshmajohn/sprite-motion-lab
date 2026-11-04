# Sprite Motion Lab

Sprite Motion Lab is a local Python project for making coherent pixel-art character animations with AI assistance. Its first use is animating the cat from Thread Cat, but the tool is intended to work with other characters too.

## Current status

The command-line prototype can create a parent directory for related sprite projects, create a new child project or initialize an existing child folder, and import a canonical PNG into that child. Each child has its own canvas dimensions. Sprite import keeps the original file unchanged, fully decodes the saved copy, and records its dimensions and SHA-256 hash. Exact nontransparent RGBA colors can be extracted as a candidate palette. Palette approval, timeline preview, export, and the browser UI are still planned. Later work will add storyboard choices, retained frame versions, and adaptive gap smoothing.

## Development setup

This workspace uses an owner-managed virtual environment at `./.venv`. Use `.venv/bin/python` to run Python and `.venv/bin/pip` to install packages. Install the recorded dependencies from the repository root with:

```sh
.venv/bin/pip install -r requirements.txt
```

From the repository root, create a parent directory with default canvas dimensions for its child projects:

```sh
.venv/bin/python -m sprite_motion_lab create "Cat Animations" --width 64 --height 64
```

This prints `PARENT_DIR` under ignored `project_data/`. To place it elsewhere, add `--storage-dir "/path/to/storage"` to `create`.

To **create a new child project**, run:

```sh
.venv/bin/python -m sprite_motion_lab add-project "PARENT_DIR" "Pouncing Cat" --width 48 --height 48
```

To **initialize a child folder you already made** inside that parent, run instead:

```sh
mkdir "PARENT_DIR/Pouncing Cat"
.venv/bin/python -m sprite_motion_lab import-project "PARENT_DIR/Pouncing Cat" --width 48 --height 48
```

Skip `mkdir` if the folder already exists. Replace `PARENT_DIR` with the path printed by `create`. Both project commands print `CHILD_DIR`. After either one, import the sprite separately, inspect the child, and run the offline tests:

```sh
.venv/bin/python -m sprite_motion_lab import-sprite "CHILD_DIR" "/absolute/path/to/cat.png"
.venv/bin/python -m sprite_motion_lab show "CHILD_DIR"
.venv/bin/python -m sprite_motion_lab show-palette "CHILD_DIR"
.venv/bin/python -m unittest discover -s tests -v
```

Replace `CHILD_DIR` with the printed child path and the PNG path with your local file. Omit the project commands' `--width` and `--height` options to inherit the parent's defaults. `import-sprite` leaves the child's saved canvas settings unchanged. `show-palette` counts exact RGBA values, excludes fully transparent pixels, and reports partially transparent colors separately. The extracted colors are candidates only; palette editing, approval, and persistence come next.

## Project documents

The [product specification](docs/PROJECT.md), [workflows](docs/UX_AND_WORKFLOWS.md), [architecture](docs/ARCHITECTURE.md), [model strategy](docs/MODEL_STRATEGY.md), and [build guide](docs/BUILD_GUIDE.md) describe the intended system. See [decisions](docs/DECISIONS.md) and [learning notes](docs/LEARNING.md) for the evolving rationale and experiments.
