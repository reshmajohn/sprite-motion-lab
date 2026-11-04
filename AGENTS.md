This workspace uses a Python virtual environment at ./.venv.

Always run Python with .venv/bin/python and install packages with .venv/bin/pip install <pkg>. Never use the system python or pip.

When you install a package, also add it to requirements.txt.

# Sprite Motion Lab — Standing instructions for Codex

> **Read this file for every Sprite Motion Lab task.** Keep it short. Do **not** edit, rewrite, replace, or automatically regenerate `AGENTS.md` during normal project work. If an instruction appears outdated, explain the proposed change to the owner and leave this file untouched. It may be changed only during a separate, explicit owner-requested documentation-maintenance task.

## Project in brief

**Project name:** Sprite Motion Lab. Keep this name unless the owner explicitly decides to rename it later.

Sprite Motion Lab is a **learning-first, local tool for designing coherent pixel-art character animations with AI assistance**. It is being created first to help the owner animate the pixel cat used by the separate Thread Cat macOS application, but it should remain reusable for later characters and projects.

The owner is comfortable describing the complete action and its personality but may not know how to draw every pose or how many frames are needed. The product must preserve AI creativity while giving the owner control over continuity, timing, palette, revisions, and final selection. The owner supplies or approves a canonical character sprite and palette, describes an overall action, chooses among AI-proposed storyboards, generates important poses, and progressively smooths gaps between frames. Deterministic code normalizes, aligns, validates, previews, and exports the results.

**Owner's machine:** Apple M4 Max with 36 GB unified memory, PyTorch MPS available, and no local NVIDIA CUDA. Begin as a private, local Python application with a lightweight browser UI. The preferred first UI is Gradio unless an early hands-on spike shows it cannot support the required timeline/version interactions. Store metadata locally and keep generated image files on disk. Do not introduce a hosted backend for the initial product.

**Model path:** Start with a provider-independent architecture and a hosted Gemini/Nano Banana adapter for the first useful generation experiment, but never make a paid call without the owner's approval and a cost estimate. Later experiments should evaluate SDXL first, then FLUX, using IP-Adapter and ControlNet where useful. Prototype local workflows in ComfyUI; move a proven workflow into Python/Diffusers only if programmatic integration is worthwhile. Fine-tuning and LoRA are later options, not MVP requirements.

## Non-negotiable product behavior

1. **All frames are first-class.** An AI-generated in-between can later become either endpoint of another in-between request. “Key pose” is metadata, not a separate immutable object type.
2. **Frame count is adaptive.** The owner can select any gap and request “Smooth this gap.” The system inserts one or more intermediate frames and can recursively subdivide a gap until the motion looks right. The owner does not need to know the required frame count beforehand.
3. **Editing is non-destructive.** Reworking a frame creates a new saved version. Never overwrite or discard an earlier version automatically. The owner can browse, compare, restore, branch from, and activate any version later.
4. **Rework guidance is optional.** The owner may enter a specific instruction or leave it blank for a creative alternative. In either case, generation receives the overall action, canonical character, current frame, neighboring active frames, and the frame's role in the motion.
5. **Timing is separate from drawings.** A unique drawing may be held for multiple playback ticks. Duration and playback speed must not be confused with the number of generated images.
6. **Continuity changes remain reviewable.** Activating or reworking a frame marks its adjacent transitions as needing preview; it does not silently regenerate neighboring frames.
7. **The canonical character and approved palette are authoritative.** Models may propose pixels, but deterministic post-processing enforces canvas, transparency, alignment, and palette rules before export.

## How to collaborate — learning is as important as working code

1. **Teach before implementing.** Explain what is being built, why it is the next small step, and any new Python, UI, image-processing, CV, generative-model, or animation concepts. Be descriptive **without being wordy**. Use a concrete cat-animation example when useful.
2. **The owner performs setup and learns commands.** For repository creation, dependency installation, environment variables, model downloads, ComfyUI setup, and starting services, give exact commands for the owner to run personally. State where to run them, what they do, expected output, and common problems. Do not run setup for the owner by default or race ahead; wait for the result.
3. **Make small, agreed changes.** Before editing code, propose the smallest useful increment, list affected files, explain the plan, and obtain approval. Do not generate the entire application scaffold or implement future phases prematurely.
4. **After every code change, report precisely:** files/functions changed; old versus new behavior; why the change was needed; important syntax or design concepts; how the owner can run and verify it; tests actually run and their results; limitations; and one suggested next step. Separate observed behavior from expected behavior.
5. **Respect cost, privacy, and ownership.** Do not make paid API calls, create cloud resources, upload private art, install large frameworks, or download model checkpoints without approval. Never commit credentials. Preserve original sprites. Confirm the license and terms of every model, checkpoint, adapter, dataset, and reference asset before redistribution or training.
6. **Keep the system understandable.** Prefer small modules, typed data, tests, and native provider APIs. Do not add LangChain, LlamaIndex, RAG, Postgres, Kubernetes, microservices, or GPU orchestration for resume value. The UI must call the same application services that tests can call without a browser.
7. **Keep documentation current in the proper file.** Record durable decisions in `docs/DECISIONS.md` and learning notes in `docs/LEARNING.md`. Update requirement, architecture, model, or build documents when an agreed implementation materially changes them. Do not grow this file with routine notes.
8. **Create and maintain README.md.** The repository should have a concise public-facing README explaining the project, current status, verified setup and run instructions, major features, and links to the detailed documents under `docs/`. Do not duplicate all planning documentation in the README or claim unfinished features work.

**Typical response pattern:** small goal → concise concept explanation → proposed files/commands → owner approval → agreed implementation → tests/observations → one next step → stop for feedback.

## Credentials, billing, ignored files, and live tests

1. **The owner manages credentials and billing.** The owner—not Codex—creates Gemini API keys, links billing, prepays credits, and sets project spend caps. Codex may explain the steps but must not create, rotate, delete, reveal, or change credentials or billing resources. Before the first live call in a session, remind the owner to confirm the prepaid balance and low project-level spend cap; the Google Tier 1 ceiling is not the project's intended budget.
2. **Read the key only through the environment.** Application code must obtain the real key from `GEMINI_API_KEY` (or the provider SDK's documented environment mechanism). Never hard-code it, place it in configuration committed to Git, include it in a prompt, send it to any service except the intended Gemini endpoint, or expose it in a browser/frontend bundle.
3. **The owner creates the real `.env`.** Codex may create `.env.example` containing only `GEMINI_API_KEY=` and explanatory comments. Codex must not create, populate, edit, open, read, print, search, summarize, or display `.env` or its value. If the key is missing, tell the owner how to create/fill `.env` personally; never ask them to paste the key into chat. Code may report only a boolean such as “Gemini key configured: yes/no.”
4. **Create protective ignore rules during initial setup.** Codex must create `.gitignore` before any secret or generated project data is added. At minimum it must contain:

   ```gitignore
   .env
   .env.*
   !.env.example
   .venv/
   __pycache__/
   *.pyc
   .pytest_cache/
   project_data/
   generated/
   ```

   Codex may use `git check-ignore .env` or equivalent to verify that the filename is ignored, but must never inspect the file contents. `.gitignore` prevents accidental commits; it is not a permission boundary for local tools.
5. **Tests are offline by default.** Normal unit and integration tests must use fake/mocked planner and renderer providers and must require neither an API key nor payment. A routine test command must never make an external model call.
6. **Live provider tests are explicit and minimal.** Mark them separately (for example, `live`), skip them by default, and require an explicit owner-controlled opt-in. Before Codex runs one, state the provider/model, number and resolution of requested images, reference images that will leave the machine, estimated maximum cost, and exact test command; then obtain approval. Begin with one request and do not automatically retry, fan out candidates, or run the full suite after success or failure.
7. **Codex may execute code that consumes the key without revealing it.** The local Python process may load `GEMINI_API_KEY` and call Gemini after approval. Logs, exceptions, saved request records, screenshots, and test output must redact credentials. Do not print the environment, dump request headers, or enable verbose HTTP logging that could reveal secrets.
8. **Treat exposure as an incident.** If a real key appears in source, Git history, terminal output, logs, chat, or a screenshot, stop live work, tell the owner to revoke/rotate it in Google AI Studio, and propose a safe cleanup plan. Do not rewrite Git history or delete files without explicit approval.

## Read deeper only when relevant

- [`docs/PROJECT.md`](docs/PROJECT.md): product purpose, users, scope, complete workflow, requirements, constraints, assets, and success criteria.
- [`docs/UX_AND_WORKFLOWS.md`](docs/UX_AND_WORKFLOWS.md): UI structure, storyboard selection, timeline operations, adaptive smoothing, version browsing, rework, timing, preview, and export behavior.
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md): proposed stack, component boundaries, provider abstraction, storage and data model, generation runs, image processing, validation, and test strategy.
- [`docs/MODEL_STRATEGY.md`](docs/MODEL_STRATEGY.md): AI versus deterministic responsibilities, prompt contracts, Nano Banana path, SDXL/FLUX/IP-Adapter/ControlNet path, ComfyUI/Diffusers roles, evaluation, cost, and fine-tuning policy.
- [`docs/BUILD_GUIDE.md`](docs/BUILD_GUIDE.md): incremental phases, exit criteria, first Codex assignment, verification strategy, and implementation conventions.
- [`docs/DECISIONS.md`](docs/DECISIONS.md): accepted design decisions, assumptions, and open questions. Do not silently reverse an accepted decision.
- [`docs/LEARNING.md`](docs/LEARNING.md): concise concept explanations, research links, and dated learning/experiment log.

## First action in a new repository

Start with **Phase 0 and the first vertical slice** in `docs/BUILD_GUIDE.md`. Explain the goal and give the owner prerequisite-check commands to run. The first approved scaffold must include `.gitignore` and a keyless `.env.example`, but never a populated `.env`. Do not create the whole scaffold, install dependencies, call an API, or download a model before the owner agrees to that specific step. The first slice must prove local project creation, canonical-sprite import, palette extraction/approval, and deterministic preview/export before relying on AI generation.
