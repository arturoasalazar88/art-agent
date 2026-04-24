# PIPELINE CONTEXT — Survival Horror Game
# This file is intended to be read by AI agents (Claude Code, OpenCode, Gemini CLI)
# It describes the complete workflow, roles, tools, and rules of the project.

---

## Project

A survival horror video game built with Three.js and Blender.
Local LLM infrastructure on Debian server handles all creative and technical AI work.
The human (referred to as YOU) is the director — makes all creative decisions.

---

## Infrastructure

| Service | URL | Purpose |
|---|---|---|
| llama-server | http://10.1.0.105:8012 | LLM inference — all text models |
| ComfyUI | http://10.1.0.105:8188 | Image generation |
| MCP server | http://10.1.0.105:8189 | Pipeline automation (pending implementation) |
| Open WebUI | http://10.1.0.105:3000 | Chat UI for human interaction with LLMs |

Switch command: `~/switch-model.sh [ornstein|supergemma|trevorjs|vision|image]`

---

## Actors and Roles

### YOU (human director)
- Makes all creative decisions
- Defines story, aesthetic, characters, scenes
- Uses Open WebUI to interact with local LLMs
- Instructs the engineer agent on what to execute

### SUPERGEMMA (local LLM — uncensored)
- Model: supergemma4-26b-uncensored-fast-v2-Q4_K_M.gguf
- Role: raw creative generation — lore, dark dialogue, creatures, horror scenes
- No content restrictions
- Output often needs post-processing by Ornstein

### TREVORJS (local LLM — uncensored)
- Model: gemma-4-26B-A4B-it-uncensored-Q4_K_M.gguf
- Role: grotesque visual content, body horror, extreme visual prompts
- No content restrictions
- Best for visual prompt generation for storyboard and assets

### ORNSTEIN (local LLM — structured)
- Model: Ornstein-26B-A4B-it-Q4_K_M.gguf
- Role: narrative structure, technical briefs, 3D asset specs, clean prompt formatting
- Used as the bridge between raw creative output and production-ready documents
- Best for: character sheets, level design docs, Blender briefs, Three.js integration specs

### SUPERGEMMA VISION (local multimodal LLM)
- Model: supergemma4-26b-abliterated-multimodal-Q4_K_M.gguf + mmproj
- Role: analyze reference images — extract palette, composition, mood, visual style
- Output: structured technical description used to guide prompt generation
- Context: 4096 tokens, mmproj runs on CPU via --override-tensor ".*=CPU"

### COMFYUI (image generation)
- Models: Pony Diffusion V6 XL + sdxl_vae.safetensors
- LoRAs: horror_style (0.7), gore_details (0.5), dark_fantasy_arch (0.4)
- Resolution: 1024x1024, 25 steps, CFG 7, sampler euler
- Workflow files: ~/ComfyUI/workflows/

### MCP SERVER (pipeline automation — pending implementation)
- Language: Python + FastMCP
- Port: 8189, transport: SSE
- Tools: save_prompt, generate_image, list_prompts, get_job_status, list_workflows, list_models
- Specs: see mcp-specs-survival-horror.md

### CLAUDE CODE / OPENCODE / GEMINI CLI (engineer agent — YOU ARE THIS)
- Role: technical execution only
- Handles: game architecture, Three.js code, Blender pipeline, MCP implementation, asset organization
- NEVER generates or modifies creative content (prompts, lore, story)
- NEVER reads prompt content from disk — only passes file paths to MCP tools

---

## The Separation Contract

THE ARTIST (YOU + local uncensored LLMs):
- Generates all creative content
- Saves prompts to disk via MCP save_prompt tool
- Never touches ComfyUI directly

THE ENGINEER (agent — Claude Code / OpenCode / Gemini CLI):
- Reads prompts from disk by file path only
- Executes generation via MCP generate_image tool
- Never reads, logs, displays, or processes prompt content
- Handles all technical failures, retries, and file organization

---

## Asset Directory Structure

```
~/horror-game/
├── assets/
│   ├── storyboard/          # frame1.json, frame1.png, frame2.json ...
│   ├── characters/          # antagonist.json, antagonist.png ...
│   ├── environments/        # hospital_corridor.json, hospital_corridor.png ...
│   └── workflows/           # ComfyUI workflow templates
├── src/                     # Three.js game source
├── models/                  # 3D models from Blender
└── docs/                    # lore, character sheets, level design docs
```

---

## Prompt File Schema

Every prompt saved by the artist is a JSON file:

```json
{
  "version": "1.0",
  "created_at": "ISO8601",
  "category": "storyboard|characters|environments",
  "name": "frame3",
  "path": "storyboard/frame3",
  "prompt": "<CONTENT — ENGINEER MUST NOT READ THIS FIELD>",
  "negative_prompt": "<CONTENT — ENGINEER MUST NOT READ THIS FIELD>",
  "metadata": {
    "scene": "description safe for engineer to read",
    "notes": "production notes"
  },
  "generation": {
    "workflow": "storyboard_base",
    "width": 1024,
    "height": 1024,
    "steps": 25,
    "cfg": 7.0,
    "seed": null
  },
  "output": {
    "image_path": null,
    "job_id": null,
    "generated_at": null
  }
}
```

---

## Complete Pipeline Flow

### Phase 1 — Aesthetic Research
1. YOU uploads reference images to Open WebUI with supergemma-vision active
2. supergemma-vision analyzes: palette, composition, lighting, mood, horror elements
3. YOU iterates until the visual aesthetic of the game is defined
4. Result: aesthetic_base.md saved to docs/

### Phase 2 — Lore and Narrative
1. YOU prompts SuperGemma for raw creative content: lore, characters, scenes
2. YOU prompts Ornstein to structure that content into production documents
3. Result: character sheets, story beats, level descriptions saved to docs/

### Phase 3 — Storyboard (Artist side)
1. YOU prompts TrevorJS or SuperGemma to generate a detailed visual prompt for a frame
2. YOU instructs the local model to call MCP save_prompt with the result
3. MCP saves the prompt to assets/storyboard/frameN.json
4. Engineer agent is NEVER involved in this phase

### Phase 4 — Image Generation (Engineer side)
1. YOU tells the engineer agent: "generate the image for storyboard/frame3"
2. Engineer calls MCP generate_image("storyboard/frame3", "storyboard_base")
3. MCP reads the JSON, injects prompt into ComfyUI workflow internally
4. ComfyUI generates the image
5. MCP saves result to assets/storyboard/frame3.png
6. Engineer reports success or technical error — never mentions prompt content

### Phase 5 — Game Development
1. YOU defines game systems, level logic, interactivity requirements
2. Engineer agent (Claude Code) implements in Three.js
3. Ornstein generates Blender briefs for 3D assets
4. Engineer handles import pipeline from Blender to Three.js
5. Engineer audits code, fixes bugs, manages build

---

## Engineer Agent Rules

1. You are the engineer — technical execution only
2. NEVER generate lore, story, dialogue, or visual prompts
3. NEVER read or display the `prompt` or `negative_prompt` fields from JSON files
4. NEVER suggest changes to creative content
5. When given a task like "generate image for frame3": call MCP, report result
6. When given a task like "write the story for level 2": decline, ask YOU to use local LLMs
7. Always verify files exist before calling generation tools
8. Handle ComfyUI downtime, timeouts, and missing models gracefully
9. Keep asset directory organized — use the defined structure
10. Update output fields in prompt JSON after successful generation

---

## Hardware Context

- GPU: RTX 3060 12GB VRAM — hybrid mode with 32GB RAM
- Only ONE model can be active at a time (llama-server OR ComfyUI, not both)
- ctx-size limit: 8192 tokens for Q4_K_M models — 16384 causes SEGV
- Vision model uses --override-tensor ".*=CPU" due to VRAM constraints
- Switch models with: ~/switch-model.sh [mode]

---

## Active Model Presets

All LLM services run on port 8012 with:
--n-gpu-layers 999 --n-cpu-moe 12 --ctx-size 8192 --flash-attn on --jinja

Vision model uses:
--ctx-size 4096 --override-tensor ".*=CPU"

ComfyUI runs on port 8188 separately — llama-server must be stopped first.
