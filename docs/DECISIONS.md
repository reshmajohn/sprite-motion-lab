# Sprite Motion Lab — Decisions and open questions

This file records durable product and architecture choices. Codex should not silently reverse an accepted decision. Add a dated entry when an experiment changes one.

## Accepted decisions

| Date | Decision | Reason | Revisit when |
| --- | --- | --- | --- |
| 2026-11-03 | Use a two-pass creative workflow: storyboard/key poses first, continuity/in-betweens second. | Preserves the creativity the owner liked while providing stronger transition constraints. | Testing shows a different decomposition is clearer or more consistent. |
| 2026-11-03 | The owner describes the complete action; the planner proposes beats and approximate timing. | The owner should not need animation expertise or exact per-frame instructions. | Planner proposals repeatedly require more work than manual beat entry. |
| 2026-11-03 | Frame count is adaptive rather than required input. | The needed drawing count is discovered through playback and gap smoothing. | Automated motion planning becomes reliable enough to offer a better default. |
| 2026-11-03 | Every frame slot has identical capabilities, regardless of whether it began as a key pose or generated in-between. | Any generated frame may later be used as an endpoint for additional interpolation. | Do not revisit without a concrete data-integrity problem. |
| 2026-11-03 | Frame versions are immutable and retained; one version is active. | The owner wants to compare earlier results and reconsider decisions later. | Storage growth becomes material; add archival/cleanup without changing default preservation. |
| 2026-11-03 | Rework instructions are optional. | Sometimes the owner knows the correction; sometimes creative variation is preferred. | Never remove the unguided option. |
| 2026-11-03 | Timing is separate from unique drawings. | Animation rhythm often comes from holds, not additional generated images. | Do not revisit. |
| 2026-11-03 | Start local and private with a lightweight visual UI. | Visual comparison and timeline operations are central; a CLI alone is insufficient. | A particular UI framework may change after an evidence-based spike. |
| 2026-11-03 | Begin model experiments without fine-tuning. | Prompting, references, structural controls, and deterministic processing should be evaluated first. | A clean licensed dataset exists and repeated identity/style failure is measured. |
| 2026-11-03 | Use a hosted Nano Banana adapter for early creative testing, with explicit cost approval. | It already produced creative ideas the owner liked and supports reference-based editing. | Pricing, terms, quality, or provider availability changes. |
| 2026-11-03 | Future local path: SDXL first, FLUX next; prototype controls in ComfyUI; integrate proven flow with Diffusers if useful. | SDXL has a mature control ecosystem; FLUX is a stronger but heavier comparison; ComfyUI makes experimentation visible. | Hardware tests or current model ecosystems favor a different order. |
| 2026-11-03 | Palette is owner-approved and enforced deterministically. | Generative output should not silently redefine the character palette. | A project explicitly opts into model-proposed palette exploration. |
| 2026-11-03 | Sprite Motion Lab remains separate from Thread Cat. | It should be reusable and should not complicate the native macOS app. | Integration should remain file-based unless a real workflow requires more. |
| 2026-11-03 | Create and maintain a public-facing `README.md` as part of the repository. | Keep detailed planning in `docs/` and include only verified features and instructions in the README. |

## Working assumptions

- Working title is **Sprite Motion Lab**; the owner has not finalized the public name.
- Default target canvas is 64×64 but must be configurable.
- Gradio is the first UI candidate, not an irreversible choice.
- Metadata should use SQLite and images should remain ordinary local files unless an early spike proves a simpler durable design.
- The canonical character is an owner-approved sprite, not an arbitrary internet reference.
- Visual review is the final animation-quality judgment; automated metrics only guide attention.

## Open questions

Resolve these only when their phase approaches:

1. What public project/repository name does the owner want?
2. Is 64×64 the first fixed canvas, or should the first vertical slice allow 32×32 and 48×48 immediately?
3. Does Gradio provide an acceptable version gallery and interactive timeline, or is a small custom frontend justified?
4. Which Nano Banana model/version gives the best cost/consistency balance when the first provider spike is run?
5. Should the text storyboard planner use the same Gemini request, a cheaper text model, or initially be owner-authored to minimize cost?
6. What pose guide is most practical for a quadruped pixel cat: silhouette, edge image, manually placed landmarks, rough painted mass, or a combination?
7. Which SDXL and FLUX checkpoints/adapters have compatible licenses and work acceptably on 36 GB Apple unified memory?
8. Should automatic palette quantization happen by default or present a before/after approval step for every generated version?
9. What sprite-sheet packing and metadata format will Thread Cat consume?
10. What retention/archival controls are needed if version history grows large?
