# Sprite Motion Lab — Incremental build guide

## 1. How to use this guide

Build one observable capability at a time. The owner should understand and run setup commands personally. Codex may implement only the agreed increment after explaining it and receiving approval.

Do not interpret later phases as permission to scaffold them early. Do not call paid services or download models simply because they appear here.

Each increment should end with:

- something the owner can run or inspect;
- tests proportional to the change;
- a concise explanation of behavior and code;
- a recorded decision/learning note when appropriate;
- one suggested next step.

## 2. Build principles

### Build the state machine before trusting a model

Versioning, insertion, timing, storage, and export are core product behavior. Prove them using imported placeholder frames and fake providers before spending money or debugging model quality.

### One vertical path before broad features

Prefer one complete path—create project → import sprite → build tiny timeline → preview → export—over many disconnected screens.

### Provider code is replaceable

The project must work with a fake provider. Hosted Gemini, ComfyUI, and Diffusers adapters implement the same application-level contract.

### Preserve raw data

Imported sources, raw model outputs, normalized derivatives, frame versions, generation records, and exports are distinct. Never overwrite the only copy.

## 3. Phase 0 — Repository and prerequisite checks

### Goal

Agree on the working repository name and establish the smallest Python project only after verifying the owner's tools.

### Codex behavior

1. Read all planning files.
2. Summarize the first vertical slice in a few sentences.
3. Ask whether **Sprite Motion Lab / `sprite-motion-lab`** is acceptable as the working name.
4. Give commands for the owner to check Git, Python, and the chosen environment tool. Do not run them for the owner.
5. Review the output and recommend the simplest environment approach. Prefer standard `venv` unless the owner explicitly wants another tool.
6. Propose the minimal first scaffold and wait for approval before writing it.

### Do not do yet

- no Gradio installation until the environment is agreed;
- no model/API SDK;
- no database migration framework;
- no ComfyUI, Diffusers, SDXL, or FLUX;
- no model checkpoints or cloud calls.

### Exit criteria

- project name/path confirmed;
- Python and Git versions observed;
- environment created by the owner;
- minimal test command succeeds;
- ignored local-data and secret patterns are planned.

## 4. Phase 1 — Deterministic asset vertical slice

### Goal

Create a local project, import a canonical transparent PNG, extract/approve a palette, create a simple preview from imported placeholder frames, and export a sprite sheet—without AI.

### Suggested increments

1. Define validated project settings and create/open project folder.
2. Import source asset non-destructively and record hash/dimensions.
3. Extract nontransparent colors and display them in a minimal UI or test fixture.
4. Approve/save a palette.
5. Import two or three placeholder frame images.
6. Normalize copies to target canvas using explicit anchors.
7. Set per-frame duration and render a nearest-neighbor preview.
8. Export PNG sequence, sheet, and manifest.

### Tests

- source bytes unchanged;
- transparent color excluded or represented intentionally;
- palette round-trips exactly;
- invalid dimensions give actionable error;
- nearest-neighbor operations preserve expected pixels;
- sheet dimensions and frame order are correct;
- project reopens with the same state.

### Exit criteria

The owner can visually run the complete deterministic workflow and understand where files and metadata are stored.

## 5. Phase 2 — Frame slots, versions, timing, and gaps

### Goal

Prove the non-destructive editing model before generation.

### Increments

1. Add stable frame slots and active version selection.
2. Add immutable frame versions and parent links.
3. Browse/compare versions and activate an older one.
4. Add hold duration independent of image versions.
5. Compute adjacent gaps and transition review status.
6. Insert a new slot between any two adjacent slots using imported images.
7. Mark adjacent gaps **needs preview** after active-version changes.

### Required scenarios

- activate V1 after V3 exists;
- branch V4 from V1;
- insert B between A and C, then D between B and C;
- change B's active version without deleting D or regenerating neighbors;
- save/reopen and retain the exact graph/order.

### Exit criteria

All required scenarios work using local placeholder images and automated tests.

## 6. Phase 3 — Fake planner and renderer adapters

### Goal

Exercise the entire UI and state flow without cost or nondeterminism.

### Increments

1. Define structured storyboard request/response models.
2. Add a fake planner returning two or three canned proposals.
3. Add a fake renderer copying known fixture candidates.
4. Implement key-pose candidate creation.
5. Implement **Smooth this gap** using fake output.
6. Implement guided and unguided rework from any base version.
7. Add run status: queued/running/succeeded/failed/cancelled.
8. Show estimated cost as zero for fake/local fixture runs.

### Exit criteria

The owner can complete the intended product workflow and observe version/gap behavior before an external provider is introduced.

## 7. Phase 4 — Storyboard planning

### Goal

Turn the whole action into selectable creative concepts without asking the owner for each frame.

### Approach

- Start with a provider-neutral structured planner contract.
- Decide whether the first live planner uses a low-cost text model or the same Gemini family only after checking current pricing and structured-output support.
- Validate returned JSON/structured data.
- Show proposals for selection/editing; do not generate images automatically.
- Save prompt version, model, response, and owner choice.

### Evaluation

For several actions, ask whether the proposals are meaningfully different, physically plausible, understandable, and useful without animation expertise.

## 8. Phase 5 — Hosted key-pose generation

### Goal

Generate a small set of creative poses with a Gemini/Nano Banana adapter.

### Safety/cost gate

Before implementation or use:

- check official SDK and current model lifecycle;
- check pricing and data-use/commercial terms;
- show the owner which reference images leave the machine;
- agree on a small maximum spend;
- use environment-based secrets;
- begin with one frame and one/few candidates.

### Experiment

Use one canonical cat, one selected storyboard beat, and a fixed prompt version. Preserve raw output and create reviewed normalized/palette derivatives. Record attempts, cost estimate, latency, and owner rating.

### Exit criteria

The hosted adapter can generate and persist candidates without bypassing version selection or deterministic validation.

## 9. Phase 6 — In-between generation and adaptive smoothing

### Goal

Generate a plausible intermediate drawing between any two active adjacent versions.

### Increments

1. Build endpoint-conditioned request with whole-action context and progress `t`.
2. Generate one midpoint candidate batch.
3. Insert selected candidate in a new slot.
4. Preview the affected region.
5. Repeat smoothing on either sub-gap.
6. Add optional transition-specific instruction.
7. Record endpoint version ids so stale outputs are detectable.

### Required proof

Start with A→C, insert B, and then insert D between B→C where B itself was generated. This directly verifies the owner's main continuity concern.

### Exit criteria

Recursive subdivision works without distinguishing original key poses from generated frames.

## 10. Phase 7 — Rework and comparison

### Goal

Allow guided or creative rework from any retained version and select the best result later.

### Increments

1. Rework dialog with optional instruction.
2. Base-version selection.
3. Automatic inclusion of canonical character, action, beat, and active neighbors.
4. Branch creation and immutable provenance.
5. Version gallery, A/B comparison, and temporary animation preview.
6. Activate selected result and invalidate adjacent transition review status.

### Exit criteria

The owner can branch from an older version, compare all alternatives, and switch active versions after later work without data loss.

## 11. Phase 8 — Quality assistance and export hardening

### Possible increments

- background/alpha checks;
- exact canvas and palette validation;
- bounding-box/centroid/ground-line warnings;
- before/after palette comparison;
- onion skin or A/B toggle;
- transition status and review checklist;
- configurable sheet packing and metadata for Thread Cat;
- export snapshots and hashes;
- Aseprite-friendly interchange.

Automated scores must remain warnings. Do not obscure a result the owner prefers merely because a metric is high.

## 12. Phase 9 — ComfyUI + SDXL learning experiment

### Goal

Reproduce one constrained frame-generation task locally and understand each component.

### Owner-approved setup only

Codex must check current official installation guidance and Apple Silicon compatibility before giving commands. The owner runs the commands. Avoid unreviewed custom nodes and unknown checkpoints.

### Experiment sequence

1. Baseline SDXL image-to-image using canonical reference.
2. Add a compatible IP-Adapter and tune appearance strength.
3. Create a rough silhouette/edge guide for one target pose.
4. Add a compatible ControlNet.
5. Compare identity, pose, palette conversion, memory, latency, and artifacts.
6. Save workflow JSON, checkpoint/adapters/licenses, settings, and contact sheet.

Do not integrate ComfyUI into the app until a workflow produces useful output repeatedly.

## 13. Phase 10 — FLUX comparison

### Goal

Evaluate one hardware-appropriate FLUX workflow against the same fixed task.

Verify exact model license, memory requirements, MPS support, IP-Adapter/ControlNet compatibility, and checkpoint provenance. Do not assume the SDXL node graph is portable.

Compare with the same rubric rather than subjective memory. Record whether quality improvement justifies heavier compute or more fragile controls.

## 14. Phase 11 — Local integration

Choose one approach only after experiments:

- **ComfyUI API adapter:** fastest path if the saved workflow is reliable and acceptable as a separate local process.
- **Diffusers adapter:** stronger programmatic ownership if all required components are supported and run acceptably on the machine.

The adapter must satisfy the same provider-neutral contract and produce ordinary generation/version records.

## 15. Phase 12 — Optional LoRA investigation

This phase requires explicit approval and evidence from earlier phases.

Prerequisites:

- measurable identity/style problem;
- owner-created or explicitly training-licensed dataset;
- train/validation split and success criteria;
- reviewed base-model and output terms;
- hardware/cloud cost estimate;
- baseline results for comparison.

Start with identity/style LoRA only. Do not claim it teaches animation continuity.

## 16. Implementation conventions

- Type public function parameters/returns.
- Keep provider payloads at adapter boundaries.
- Use stable ids; never use UI frame number as identity.
- Treat frame image versions as immutable.
- Make filesystem/database changes transactional where practical.
- Hash imported and generated assets.
- Store relative project paths, not machine-specific absolute paths, when possible.
- Use explicit nearest-neighbor operations; never rely on library defaults.
- Prefer small pure functions for image processing.
- Inject providers so tests use fakes.
- Record schema/prompt versions.
- Never log secrets or raw authorization data.
- Avoid premature async queues; add background execution only when UI blocking becomes a measured problem.

## 17. First Codex assignment

When these files are placed in a new repository, Codex should:

1. read `AGENTS.md` and the linked planning documents;
2. summarize the first vertical slice and confirm the provisional name;
3. explain why deterministic import/palette/preview/export comes before AI;
4. give the owner prerequisite-check commands for Git and Python to run;
5. wait for the output;
6. propose the smallest scaffold and affected files;
7. obtain approval before creating code.

After the owner approves the initial scaffold, create a minimal `README.md` describing the project and current development status. Do not include unverified setup instructions. Do not call Gemini or install ComfyUI in this assignment.

## 18. Definition of done for any increment

- requested behavior is demonstrable;
- existing project data remains readable;
- tests were added/run where practical;
- actual test results are reported;
- no paid/unapproved action occurred;
- relevant docs/decision log updated if the design changed;
- owner receives exact run/verification commands;
- limitations and next step are clear.
