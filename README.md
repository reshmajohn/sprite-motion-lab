# Sprite Motion Lab

Sprite Motion Lab is a local Python project for making coherent pixel-art character animations with AI assistance. Its first use is animating the cat from Thread Cat, but the tool is intended to work with other characters too.

## Current status

Local project creation and reopening now work through a small command-line entry point. Sprite import, palette approval, timeline preview, export, and the browser UI are still planned. Later work will add storyboard choices, retained frame versions, and adaptive gap smoothing.

## Development setup

This workspace uses an owner-managed virtual environment at `./.venv`. Use `.venv/bin/python` to run Python and `.venv/bin/pip install <pkg>` to install a package, recording installed packages in `requirements.txt`. This increment requires no third-party packages.

From the repository root, create a project and run the offline tests:

```sh
.venv/bin/python -m sprite_motion_lab create "Cat Study"
.venv/bin/python -m unittest discover -s tests -v
```

The create command prints the new path under ignored `project_data/`. Pass that path to `.venv/bin/python -m sprite_motion_lab show` to read the saved name and canvas dimensions. The default canvas is 64×64; `create` also accepts `--width` and `--height`.

## Project documents

The [product specification](docs/PROJECT.md), [workflows](docs/UX_AND_WORKFLOWS.md), [architecture](docs/ARCHITECTURE.md), [model strategy](docs/MODEL_STRATEGY.md), and [build guide](docs/BUILD_GUIDE.md) describe the intended system. See [decisions](docs/DECISIONS.md) and [learning notes](docs/LEARNING.md) for the evolving rationale and experiments.
