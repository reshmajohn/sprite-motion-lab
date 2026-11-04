# Sprite Motion Lab — Learning notes and experiment log

Use this file for concise concept explanations, useful links, and dated observations from real experiments. Do not paste large tutorials or model marketing claims. Distinguish observed results from expectations.

## 1. Concept map

### Sprite, frame, timing, and animation

- **Sprite:** one raster character image, usually small and palette-limited.
- **Frame slot:** one ordered position in an animation timeline.
- **Frame version:** one candidate image for that slot.
- **Key pose:** an important storytelling/extreme pose; in this app it is metadata, not a different data type.
- **In-between:** a drawing connecting two poses. It is not a pixel blend; anatomy must be redrawn plausibly.
- **Hold:** showing the same drawing for longer. More playback time does not require more generated images.
- **Anticipation:** preparation before a main action, such as crouching before a leap.
- **Follow-through/settle:** motion after the main action that resolves momentum and personality.
- **Onion skin:** faint display of neighboring frames to compare placement and movement.

### Palette and pixel processing

- **Palette extraction:** normal code counts/organizes colors from an approved sprite; it does not decide which colors the owner likes.
- **Quantization:** maps many generated colors to a smaller approved set.
- **Nearest-neighbor scaling:** enlarges pixels without smoothing them.
- **Alpha channel:** per-pixel transparency. White pixels are not automatically transparent.
- **Anchor/alignment:** consistent reference such as ground contact or body center used to reduce apparent jumping.

### Generative image tools

- **Foundation image model:** a large pretrained generator/editor, such as SDXL, FLUX, or Google's hosted image models.
- **Nano Banana:** Google's hosted Gemini image-generation/editing family; accessed through the Gemini API, not Ollama and not currently the same as any Amazon Bedrock image model.
- **SDXL:** an open-weight Stable Diffusion family with a mature ecosystem of adapters and controls.
- **FLUX:** a newer image-model family known for strong prompt following, with variants that differ in size, license, and hardware needs.
- **IP-Adapter:** adds image-reference conditioning, useful for appearance/style/identity guidance.
- **ControlNet:** adds structural conditioning such as edges, pose, depth, or segmentation.
- **LoRA:** a small trained adapter that can teach a style or character appearance to a compatible base model. It does not automatically teach motion.
- **Denoising strength:** in image-to-image generation, controls how much the model may depart from the input.
- **Seed:** initial randomness value; useful for comparisons, though exact reproducibility can still vary by stack/hardware.

### Workflow tools

- **ComfyUI:** a visual node-based environment for assembling and testing generation pipelines.
- **Diffusers:** a Python library for running and combining compatible generative-model components in code.
- **Ollama:** a convenient local model runner with some image-generation support; useful for simple inference but not the primary fine-control workbench here.
- **Gradio:** a Python UI toolkit suitable for a local prototype of image workflows.

## 2. Why the original generated sheets looked choppy

The Nano Banana sheets contained appealing individual ideas but behaved like a set of separate illustrations. Across frames, the cat's size, anatomy, markings, perspective, ground position, tail, and relationship to the yarn changed too much. A white background, border, JPEG compression, and inconsistent spacing also made them unsuitable as production sprite sheets.

The solution is not merely “ask for more frames.” It is to provide:

- one canonical identity and palette;
- whole-action context;
- selected key poses;
- both endpoints for each in-between;
- explicit relative progress;
- deterministic normalization;
- non-destructive iteration and playback review.

## 3. Why generated sheets are not the preferred unit

A single model call can create a multi-frame sheet cheaply, but individual poses may drift and are hard to revise independently. The preferred unit is one candidate image linked to a frame slot/version, even if the UI later supports efficient batches. Packing happens after selection.

## 4. Why fine-tuning comes later

Fine-tuning can hide weaknesses in prompts, references, structure guides, or post-processing. It also needs a clean licensed dataset and evaluation baseline. First test reference conditioning, endpoint-aware prompts, IP-Adapter, ControlNet, and palette/alignment processing. Only then can a LoRA experiment answer a specific measured question.

## 5. Research starting points

- Gemini image generation: <https://ai.google.dev/gemini-api/docs/image-generation>
- Gemini API pricing: <https://ai.google.dev/gemini-api/docs/pricing>
- Diffusers IP-Adapter: <https://huggingface.co/docs/diffusers/main/using-diffusers/ip_adapter>
- Diffusers ControlNet: <https://huggingface.co/docs/diffusers/main/using-diffusers/controlnet>
- Diffusers FLUX pipelines: <https://huggingface.co/docs/diffusers/main/api/pipelines/flux>
- ComfyUI documentation: <https://docs.comfy.org/>

Before following any guide, verify that it matches the exact model, checkpoint, operating system, and current library versions.

## 6. Experiment log template

Append entries using this structure:

```markdown
### YYYY-MM-DD — Short experiment title

**Question:** What are we trying to learn?

**Setup:** Model/version, adapter/checkpoint, hardware, prompt version,
references, seed, dimensions, important parameters, and license links.

**Observed result:** What actually happened, including failures.

**Owner rating:** Creativity, identity, pose, continuity, palette conversion,
latency, and cost.

**Decision:** What changes, if anything, and what should be tested next?
```

## 7. Initial recorded understanding — 2026-11-03

- The owner values the model's creative staging and does not want to invent every intermediate pose.
- The system should plan at the action/beat level and constrain continuity at the frame-gap level.
- Recursive gap smoothing solves unknown frame count while preserving control.
- Any generated frame can become a future interpolation endpoint.
- Versions must be retained because a previously rejected or superseded result may later look best.
- Rework guidance must be optional.
- A UI is required for timeline, preview, version comparison, and iterative refinement.
- Hosted Nano Banana is the first practical creativity benchmark; SDXL/FLUX with ComfyUI are the future learning and local-control path.

## 8. PNG decoding and RGBA palette extraction — 2026-11-04

- A valid PNG header describes the image but does not prove that its pixel data is complete. Pillow now verifies and decodes the entire file before import succeeds.
- RGBA stores red, green, blue, and alpha for each pixel. Alpha `0` is fully transparent; values from `1` through `255` remain visible and are counted as distinct colors.
- Candidate colors are sorted by pixel count and then RGBA value. This makes the output deterministic while leaving palette approval to the owner.
