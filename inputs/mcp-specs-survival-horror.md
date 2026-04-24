# MCP Server Specs — Survival Horror Pipeline
## Technical Specification Document

**Version:** 1.0  
**Project:** Survival Horror Game — Artista / Ingeniero Pipeline  
**Development Workflow:** Claude Code (design + audit) → OpenCode + Codex (implementation)  
**Status:** Ready for implementation

---

## 1. Project Context

This document specifies two MCP (Model Context Protocol) servers that form the bridge between the creative pipeline (LLM local models via llama-server) and the technical execution pipeline (ComfyUI image generation). The architecture enforces a strict separation between creative content generation and technical execution so that censored AI agents (Claude Code, Gemini CLI) can operate the technical pipeline without ever reading or generating uncensored creative content.

### 1.1 Infrastructure

| Component | Location | Address |
|---|---|---|
| llama-server (LLM) | Debian server | `http://10.1.0.105:8012` |
| ComfyUI | Debian server | `http://10.1.0.105:8188` |
| MCP Server | Debian server | `http://10.1.0.105:8189` |
| Open WebUI | Debian server | `http://10.1.0.105:3000` |
| Client machines | Mac mini / MacBook | SSH + browser |

### 1.2 The Separation Contract

```
THE ARTIST (creative, uncensored)
  Open WebUI + llama-server local models
  Generates prompts → saves to disk via MCP
  NEVER touches ComfyUI directly

THE ENGINEER (technical, censored-safe)
  OpenCode / Claude Code / Gemini CLI
  Reads prompts from disk → executes generation via MCP
  NEVER reads or modifies prompt content
```

---

## 2. MCP Server Architecture

### 2.1 Single Server, Two Tool Groups

Both tool groups are served by a single MCP server process. This simplifies deployment, authentication, and client configuration.

```
mcp-horror-pipeline (port 8189)
├── Tool Group A: prompt_tools     ← used by THE ARTIST
│   ├── save_prompt
│   ├── list_prompts
│   └── get_prompt_metadata
└── Tool Group B: generation_tools ← used by THE ENGINEER
    ├── generate_image
    ├── get_job_status
    ├── list_workflows
    ├── list_models
    └── list_loras
```

### 2.2 Technology Stack

| Layer | Technology | Reason |
|---|---|---|
| Language | Python 3.11+ | Available on Debian, best MCP SDK support |
| MCP Framework | `fastmcp` | Simplest agnotic MCP server implementation |
| Transport | stdio + SSE | stdio for Claude Code/CLI tools, SSE for web clients |
| HTTP Client | `httpx` (async) | Non-blocking calls to ComfyUI and llama-server |
| Config | `pydantic-settings` | Environment-based config, no hardcoded paths |
| Logging | `structlog` | JSON structured logs for debugging |

### 2.3 Dependencies

```toml
[project]
name = "mcp-horror-pipeline"
version = "1.0.0"
requires-python = ">=3.11"

dependencies = [
    "fastmcp>=2.0.0",
    "httpx>=0.27.0",
    "pydantic-settings>=2.0.0",
    "structlog>=24.0.0",
    "aiofiles>=23.0.0",
    "python-dotenv>=1.0.0",
]
```

---

## 3. Project Structure

```
mcp-horror-pipeline/
├── src/
│   └── mcp_horror/
│       ├── __init__.py
│       ├── server.py              # MCP server entrypoint
│       ├── config.py              # Settings via pydantic-settings
│       ├── tools/
│       │   ├── __init__.py
│       │   ├── prompt_tools.py    # save_prompt, list_prompts, get_prompt_metadata
│       │   └── generation_tools.py # generate_image, get_job_status, list_workflows
│       ├── clients/
│       │   ├── __init__.py
│       │   ├── comfyui.py         # ComfyUI REST API client
│       │   └── llama.py           # llama-server REST API client (future use)
│       └── models/
│           ├── __init__.py
│           ├── prompt.py          # Prompt schema
│           └── job.py             # Job status schema
├── assets/                        # Project assets root (created by server on startup)
│   ├── storyboard/
│   ├── characters/
│   ├── environments/
│   └── workflows/
├── tests/
│   ├── test_prompt_tools.py
│   ├── test_generation_tools.py
│   └── test_comfyui_client.py
├── .env.example
├── pyproject.toml
├── README.md
└── systemd/
    └── mcp-horror-pipeline.service
```

---

## 4. Configuration

### 4.1 Environment Variables (.env)

```env
# Server
MCP_HOST=0.0.0.0
MCP_PORT=8189
MCP_TRANSPORT=sse   # sse | stdio

# ComfyUI
COMFYUI_URL=http://127.0.0.1:8188
COMFYUI_TIMEOUT=300   # seconds, image generation can be slow

# llama-server
LLAMA_URL=http://127.0.0.1:8012
LLAMA_TIMEOUT=120

# Assets
ASSETS_ROOT=/home/asalazar/horror-game/assets
WORKFLOWS_DIR=/home/asalazar/ComfyUI/workflows

# Security
MCP_API_KEY=   # optional, leave empty to disable auth
```

### 4.2 Config Class

```python
# src/mcp_horror/config.py
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    mcp_host: str = "0.0.0.0"
    mcp_port: int = 8189
    mcp_transport: str = "sse"

    comfyui_url: str = "http://127.0.0.1:8188"
    comfyui_timeout: int = 300

    llama_url: str = "http://127.0.0.1:8012"
    llama_timeout: int = 120

    assets_root: Path = Path("/home/asalazar/horror-game/assets")
    workflows_dir: Path = Path("/home/asalazar/ComfyUI/workflows")

    mcp_api_key: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

---

## 5. Data Schemas

### 5.1 Prompt File Schema (JSON on disk)

Every saved prompt is a JSON file with this structure:

```json
{
  "version": "1.0",
  "created_at": "2026-04-23T10:00:00Z",
  "updated_at": "2026-04-23T10:00:00Z",
  "category": "storyboard",
  "name": "frame3",
  "path": "storyboard/frame3",
  "prompt": "<uncensored prompt content — never read by engineer agents>",
  "negative_prompt": "<negative prompt>",
  "metadata": {
    "scene": "hospital corridor",
    "characters": ["antagonist"],
    "mood": "oppressive",
    "notes": "any production notes safe for engineer to read"
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

**Critical:** The `prompt` and `negative_prompt` fields are write-only from the engineer's perspective. Engineer tools read the file to extract `generation` parameters but must not log, display, or process the prompt content.

### 5.2 Job Status Schema

```python
class JobStatus(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    progress: float = 0.0        # 0.0 to 1.0
    image_path: Optional[str]    # populated when completed
    error: Optional[str]         # populated when failed
    created_at: datetime
    completed_at: Optional[datetime]
```

---

## 6. Tool Specifications

### 6.1 Tool: save_prompt

**Used by:** THE ARTIST (via Open WebUI or any MCP client)  
**Purpose:** Persist a generated prompt to disk in the standard structure

```python
@mcp.tool()
async def save_prompt(
    path: str,
    prompt: str,
    negative_prompt: str = "",
    metadata: dict = {},
    generation_params: dict = {}
) -> dict:
    """
    Save a generated prompt to the assets directory.

    Args:
        path: Relative path under assets root. Examples:
              "storyboard/frame3"
              "characters/antagonist"
              "environments/hospital_corridor"
        prompt: The full prompt text (uncensored content from local model)
        negative_prompt: Negative prompt text
        metadata: Optional dict with scene notes, character names, mood.
                  Only include content safe for engineer agents to read.
        generation_params: Optional overrides for workflow defaults.
                           Keys: workflow, width, height, steps, cfg, seed

    Returns:
        {
            "success": true,
            "path": "storyboard/frame3",
            "full_path": "/home/asalazar/horror-game/assets/storyboard/frame3.json",
            "created_at": "2026-04-23T10:00:00Z"
        }
    """
```

**Behavior:**
- Creates directory structure if it does not exist
- If file already exists, updates it and bumps `updated_at`
- Validates that `path` does not contain `..` (path traversal prevention)
- Returns only safe metadata in response, never echoes the prompt back

---

### 6.2 Tool: list_prompts

**Used by:** THE ARTIST and THE ENGINEER  
**Purpose:** List available prompts, optionally filtered by category

```python
@mcp.tool()
async def list_prompts(
    category: Optional[str] = None,
    include_generated: bool = False
) -> dict:
    """
    List saved prompts in the assets directory.

    Args:
        category: Optional filter. One of: storyboard, characters, environments
                  If None, returns all categories
        include_generated: If True, include prompts that already have an output image.
                           If False, only return prompts pending generation.

    Returns:
        {
            "prompts": [
                {
                    "path": "storyboard/frame3",
                    "category": "storyboard",
                    "name": "frame3",
                    "has_image": false,
                    "workflow": "storyboard_base",
                    "created_at": "2026-04-23T10:00:00Z"
                }
            ],
            "total": 1
        }
    """
```

**Critical:** Response NEVER includes `prompt` or `negative_prompt` fields.

---

### 6.3 Tool: get_prompt_metadata

**Used by:** THE ENGINEER  
**Purpose:** Get generation parameters for a prompt without exposing content

```python
@mcp.tool()
async def get_prompt_metadata(path: str) -> dict:
    """
    Get the technical metadata and generation parameters for a prompt.
    Does NOT return prompt content.

    Args:
        path: Relative path under assets root. Example: "storyboard/frame3"

    Returns:
        {
            "path": "storyboard/frame3",
            "exists": true,
            "metadata": { "scene": "...", "notes": "..." },
            "generation": {
                "workflow": "storyboard_base",
                "width": 1024,
                "height": 1024,
                "steps": 25,
                "cfg": 7.0,
                "seed": null
            },
            "output": {
                "has_image": false,
                "image_path": null
            }
        }
    """
```

---

### 6.4 Tool: generate_image

**Used by:** THE ENGINEER (via Claude Code, OpenCode, Gemini CLI)  
**Purpose:** Execute image generation for a saved prompt

```python
@mcp.tool()
async def generate_image(
    prompt_path: str,
    workflow_name: Optional[str] = None,
    seed: Optional[int] = None,
    wait_for_completion: bool = True
) -> dict:
    """
    Generate an image for a saved prompt using ComfyUI.

    The prompt content is read internally and injected into the workflow.
    The engineer agent never sees the prompt content.

    Args:
        prompt_path: Relative path. Example: "storyboard/frame3"
        workflow_name: Override the workflow defined in the prompt file.
                       If None, uses the workflow specified in the prompt file.
        seed: Override seed. If None, uses seed from prompt file or randomizes.
        wait_for_completion: If True, blocks until image is ready (up to COMFYUI_TIMEOUT).
                             If False, returns job_id immediately for async polling.

    Returns (wait_for_completion=True):
        {
            "success": true,
            "job_id": "abc123",
            "prompt_path": "storyboard/frame3",
            "image_path": "/home/asalazar/horror-game/assets/storyboard/frame3.png",
            "elapsed_seconds": 45.2
        }

    Returns (wait_for_completion=False):
        {
            "success": true,
            "job_id": "abc123",
            "status": "queued"
        }
    """
```

**Internal flow (never exposed to engineer agent):**
1. Load prompt JSON from disk
2. Load workflow JSON from workflows directory
3. Inject `prompt` field into workflow positive CLIP node
4. Inject `negative_prompt` field into workflow negative CLIP node
5. Apply generation parameters (width, height, steps, cfg, seed)
6. POST to ComfyUI `/prompt` endpoint
7. Poll `/history/{job_id}` until complete or timeout
8. Save output image to `{assets_root}/{prompt_path}.png`
9. Update `output` fields in prompt JSON
10. Return only path and status to caller

---

### 6.5 Tool: get_job_status

**Used by:** THE ENGINEER  
**Purpose:** Poll status of an async generation job

```python
@mcp.tool()
async def get_job_status(job_id: str) -> dict:
    """
    Get the current status of a generation job.

    Args:
        job_id: Job ID returned by generate_image

    Returns:
        {
            "job_id": "abc123",
            "status": "completed",
            "progress": 1.0,
            "image_path": "/home/asalazar/horror-game/assets/storyboard/frame3.png",
            "elapsed_seconds": 45.2,
            "error": null
        }
    """
```

---

### 6.6 Tool: list_workflows

**Used by:** THE ENGINEER  
**Purpose:** List available ComfyUI workflow templates

```python
@mcp.tool()
async def list_workflows() -> dict:
    """
    List available workflow JSON files.

    Returns:
        {
            "workflows": [
                {
                    "name": "storyboard_base",
                    "path": "/home/asalazar/ComfyUI/workflows/storyboard_base.json",
                    "description": null
                }
            ]
        }
    """
```

---

### 6.7 Tool: list_models

**Used by:** THE ENGINEER  
**Purpose:** List available checkpoints and LoRAs

```python
@mcp.tool()
async def list_models() -> dict:
    """
    List available models from ComfyUI.

    Returns:
        {
            "checkpoints": ["ponyDiffusionV6XL.safetensors"],
            "loras": [
                "horror_style.safetensors",
                "gore_details.safetensors",
                "dark_fantasy_arch.safetensors"
            ],
            "vaes": ["sdxl_vae.safetensors"]
        }
    """
```

---

## 7. ComfyUI Client Implementation

```python
# src/mcp_horror/clients/comfyui.py

class ComfyUIClient:
    """
    Async client for ComfyUI REST API.
    Handles workflow injection, job queuing, and polling.
    """

    async def get_models(self) -> dict:
        """GET /object_info — extract checkpoint, lora, vae names"""

    async def queue_prompt(self, workflow: dict) -> str:
        """POST /prompt — returns prompt_id"""

    async def get_history(self, prompt_id: str) -> dict:
        """GET /history/{prompt_id} — returns job history"""

    async def get_queue(self) -> dict:
        """GET /queue — returns pending and running jobs"""

    async def wait_for_completion(
        self,
        prompt_id: str,
        timeout: int,
        poll_interval: float = 2.0
    ) -> dict:
        """Poll get_history until job complete or timeout"""

    def inject_prompt_into_workflow(
        self,
        workflow: dict,
        prompt: str,
        negative_prompt: str,
        params: dict
    ) -> dict:
        """
        Inject prompt content into workflow JSON.
        Finds CLIPTextEncode nodes by their connection to KSampler
        positive/negative inputs and replaces text content.
        Also applies width, height, steps, cfg, seed overrides.
        Returns modified workflow copy — never mutates original.
        """
```

---

## 8. Security Considerations

### 8.1 Prompt Content Isolation

- The `prompt` and `negative_prompt` fields are NEVER returned in any tool response
- They are NEVER logged at any log level
- They are read from disk, injected into workflow in memory, and the modified workflow is discarded after queuing
- The only external system that receives prompt content is ComfyUI running on localhost

### 8.2 Path Traversal Prevention

```python
def validate_asset_path(path: str, assets_root: Path) -> Path:
    """Ensure path resolves within assets_root — raise ValueError if not"""
    resolved = (assets_root / path).resolve()
    if not str(resolved).startswith(str(assets_root.resolve())):
        raise ValueError(f"Path traversal attempt detected: {path}")
    return resolved
```

### 8.3 API Key Authentication (optional)

If `MCP_API_KEY` is set in config, all requests must include:
```
Authorization: Bearer <key>
```

---

## 9. systemd Service

```ini
# /etc/systemd/system/mcp-horror-pipeline.service

[Unit]
Description=MCP Horror Pipeline Server
After=network.target

[Service]
Type=simple
User=asalazar
WorkingDirectory=/home/asalazar/mcp-horror-pipeline
EnvironmentFile=/home/asalazar/mcp-horror-pipeline/.env
ExecStart=/home/asalazar/mcp-horror-pipeline/venv/bin/python -m mcp_horror.server
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 10. Client Configuration

### 10.1 Claude Code (.claude/mcp_config.json)

```json
{
  "mcpServers": {
    "horror-pipeline": {
      "url": "http://10.1.0.105:8189/sse",
      "transport": "sse"
    }
  }
}
```

### 10.2 Gemini CLI

```json
{
  "mcp": {
    "servers": {
      "horror-pipeline": {
        "url": "http://10.1.0.105:8189/sse"
      }
    }
  }
}
```

### 10.3 OpenCode

```json
{
  "mcp": {
    "horror-pipeline": {
      "url": "http://10.1.0.105:8189/sse",
      "transport": "sse"
    }
  }
}
```

### 10.4 Open WebUI (via tool plugin)

Configure OpenAI-compatible tool endpoint pointing to MCP SSE bridge at `http://10.1.0.105:8189`.

---

## 11. Development Workflow

### Step 1 — Claude Code designs and writes specs
- This document
- Data schemas
- Tool signatures with full docstrings
- Client interface definitions
- Test specifications

### Step 2 — OpenCode + Codex implements
- Implements all tools following specs exactly
- Implements ComfyUI client
- Writes unit tests per test specifications below
- No creative decisions — spec is the source of truth

### Step 3 — Claude Code audits
- Verifies prompt content is never exposed in any code path
- Verifies path traversal prevention
- Verifies error handling covers ComfyUI downtime, timeout, missing files
- Verifies all tool signatures match specs
- Runs test suite

---

## 12. Test Specifications

### 12.1 Prompt Tools Tests

```python
# tests/test_prompt_tools.py

def test_save_prompt_creates_file()
def test_save_prompt_creates_nested_directories()
def test_save_prompt_updates_existing_file()
def test_save_prompt_rejects_path_traversal()
def test_list_prompts_filters_by_category()
def test_list_prompts_never_returns_prompt_content()
def test_get_prompt_metadata_never_returns_prompt_content()
def test_get_prompt_metadata_returns_404_for_missing_file()
```

### 12.2 Generation Tools Tests

```python
# tests/test_generation_tools.py

def test_generate_image_reads_prompt_from_disk()
def test_generate_image_injects_into_workflow()
def test_generate_image_saves_output_to_correct_path()
def test_generate_image_updates_prompt_json_with_output()
def test_generate_image_handles_comfyui_timeout()
def test_generate_image_handles_missing_prompt_file()
def test_generate_image_async_returns_job_id_immediately()
def test_get_job_status_returns_progress()
def test_list_workflows_returns_available_files()
def test_list_models_queries_comfyui_object_info()
```

### 12.3 ComfyUI Client Tests

```python
# tests/test_comfyui_client.py

def test_inject_prompt_finds_positive_clip_node()
def test_inject_prompt_finds_negative_clip_node()
def test_inject_prompt_applies_generation_params()
def test_inject_prompt_does_not_mutate_original_workflow()
def test_wait_for_completion_polls_until_done()
def test_wait_for_completion_raises_on_timeout()
```

---

## 13. Batch Generation (Future Tool)

Once the core tools are validated, add:

```python
@mcp.tool()
async def batch_generate(
    category: Optional[str] = None,
    paths: Optional[list[str]] = None,
    workflow_override: Optional[str] = None,
    skip_existing: bool = True
) -> dict:
    """
    Generate images for multiple prompts sequentially.

    Args:
        category: Generate all prompts in this category
        paths: Or specify explicit list of paths
        workflow_override: Apply same workflow to all
        skip_existing: Skip prompts that already have output images

    Returns:
        {
            "total": 5,
            "completed": 4,
            "failed": 1,
            "results": [...]
        }
    """
```

---

## 14. Summary

| Item | Value |
|---|---|
| Server | Python + FastMCP, port 8189 |
| Transport | SSE (web clients) + stdio (CLI tools) |
| Tools | 7 initial + 1 future batch tool |
| Prompt isolation | Enforced at data schema + code level |
| Compatible clients | Claude Code, OpenCode, Gemini CLI, Open WebUI |
| Deployment | systemd service on Debian server |
| Auth | Optional API key via env var |
| Assets root | `/home/asalazar/horror-game/assets` |
| Workflows dir | `/home/asalazar/ComfyUI/workflows` |
