# Sprite Motion Lab

Sprite Motion Lab is a local Python project for making coherent pixel-art character animations with AI assistance. Its first use is animating the cat from Thread Cat, but the tool is intended to work with other characters too.

## Current status

The project is at the initial repository stage. There is no runnable application yet. The first planned workflow is entirely deterministic: create a local project, import a canonical sprite, extract and approve its palette, arrange placeholder frames with hold durations, preview the motion, and export a sprite sheet. Later work will add storyboard choices, retained frame versions, and adaptive gap smoothing.

## Development setup

This workspace uses an owner-managed virtual environment at `./.venv`. Check it from the repository root with `.venv/bin/python --version`. Use `.venv/bin/python` to run Python and `.venv/bin/pip install <pkg>` to install a package, recording installed packages in `requirements.txt`. No packages or application run command are required for this initial scaffold.

## Project documents

The [product specification](docs/PROJECT.md), [workflows](docs/UX_AND_WORKFLOWS.md), [architecture](docs/ARCHITECTURE.md), [model strategy](docs/MODEL_STRATEGY.md), and [build guide](docs/BUILD_GUIDE.md) describe the intended system. See [decisions](docs/DECISIONS.md) and [learning notes](docs/LEARNING.md) for the evolving rationale and experiments.
