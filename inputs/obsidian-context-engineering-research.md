# Obsidian + Context Engineering for Full-Load Local Agent Memory

## Overview

This report evaluates a specific design pattern: using Obsidian as the authoring and maintenance layer for agent knowledge, then compiling selected notes into a compact runtime memory artifact that is fully loaded into a local LLM context window every session. The target environment is a constrained local model with an 8,192-token context window, no vector database, no semantic retrieval, and a requirement that persistent memory remain fully inspectable and file-based.[cite:36][cite:63][cite:66]

The central finding is that Obsidian is a strong fit **as a source workspace**, but not as a raw runtime memory format. Obsidian’s strengths are local Markdown files, link-based organization, frontmatter metadata, plugin-driven automation, and Git-friendly storage. Those strengths become valuable when paired with context-engineering rules that aggressively select, compress, and compile only the highest-signal notes into a bounded final memory file.[cite:66][cite:67][cite:84][cite:36]

The recommended architecture is therefore two-layered:

1. **Source layer:** an Obsidian vault for human editing, note linking, metadata, decision capture, canon maintenance, and review.[cite:66][cite:67]
2. **Runtime layer:** a generated memory snapshot such as `memory.txt`, `memory.md`, or a compact block-structured artifact optimized for the target model’s tokenizer and hard-limited by token budget.[cite:36][cite:63][cite:8]

## Why this pattern is credible

Anthropic’s context-engineering guidance explicitly treats context as the complete token payload at inference time and recommends techniques such as compaction, structured note-taking, and file-backed memory for long-horizon agent work.[cite:36][cite:63] Anthropic also describes a production pattern in Claude Code where persistent instruction files such as `CLAUDE.md` are loaded up front, while other information is maintained through compaction and external memory primitives.[cite:36][cite:63]

Letta’s memory model independently reinforces the same core idea. Its “memory blocks” are pinned in the context window, always visible to the agent, and bounded by configurable size limits so that persistent memory remains useful without overwhelming the model’s working context.[cite:2][cite:8] That is very close to the desired design goal here, except the implementation proposed in this report uses Obsidian as the upstream editing system and a custom compiler for the final runtime file.[cite:2][cite:8]

## Core conclusion

Obsidian should not be treated as the thing the model reads directly. Instead, it should be treated as a local knowledge workbench that stores richer material than the model can afford to ingest. Context engineering then becomes the compiler discipline that transforms that richer vault into a dense, minimal, bounded, always-loaded memory file.[cite:36][cite:63][cite:66]

In practical terms, the winning pattern is:

- rich notes for humans,
- strong metadata for automation,
- deterministic export rules,
- hard token ceilings,
- periodic compaction,
- and a small set of pinned memory blocks presented to the model every session.[cite:84][cite:81][cite:63][cite:8]

## Obsidian capabilities that matter

### Local Markdown storage

Obsidian stores notes as local Markdown files, which keeps the vault editable outside Obsidian and avoids lock-in. Existing Markdown folders can be opened as vaults directly, which is ideal for agent systems that also need CLI tooling, Git automation, and external compilers.[cite:66][cite:67][cite:73]

This matters because a file-based agent memory workflow needs source files that are easy to diff, lint, transform, and compile. Markdown is not the densest runtime format, but it is an excellent source format for note authoring and review.[cite:66][cite:67]

### Metadata and queryability

Dataview turns vault metadata into a queryable index over Markdown frontmatter and inline fields. It can filter, sort, and extract information from notes, and exposes a JavaScript API for more advanced generation workflows.[cite:82][cite:84]

This is valuable for memory compilation because the runtime file should not be hand-curated line by line. Instead, notes should carry metadata such as `agent`, `block`, `priority`, `stability`, `status`, `expires`, or `compile`, and the compiler should build the final memory snapshot from these metadata signals.[cite:82][cite:84]

### Templater automation

Templater supports reusable templates and JavaScript execution inside Obsidian. It can insert variables, manipulate files, rename notes, and automate note creation or transformation.[cite:74][cite:77]

That makes it well-suited for enforcing consistent note schemas such as “decision record,” “canon fact,” “constraint,” “open loop,” or “scene brief.” Consistent schemas matter because compact agent memory depends on structured, repetitive note shapes that can be summarized mechanically rather than freeform prose that has to be reinterpreted every build.[cite:74][cite:77][cite:36]

### Generating plain Markdown outputs

Dataview query results can be written back out as pure Markdown using plugin APIs and scripting patterns, which makes Obsidian capable of producing exportable, deterministic derived files rather than only interactive views.[cite:81] The Run plugin extends this idea by generating and updating Markdown content from Dataview and JavaScript expressions inside Obsidian.[cite:59]

This is important because a high-quality agent memory system should not rely on Obsidian’s UI at inference time. It should emit a plain file that any local runtime can read, count, validate, and inject into the prompt.[cite:59][cite:81][cite:66]

### Git integration

The Obsidian Git plugin brings Git-based version control into the vault, including automatic commit-and-sync, source control views, and history inspection.[cite:75][cite:78] Developers also commonly open a Git repository directly as an Obsidian vault, which means the note system fits naturally into existing engineering workflows.[cite:72]

This is especially useful for persistent memory because every compaction event becomes auditable. When a memory compiler rewrites facts, folds decision logs into canon, or removes stale entries, Git provides a safety net for inspection and rollback.[cite:75][cite:72]

## Context-engineering principles that make the pattern work

Anthropic frames context engineering as optimizing the full token payload supplied to the model, not merely editing the system prompt. The main discipline is to find the smallest high-signal set of tokens that still produces the desired behavior.[cite:36]

For full-load memory systems, five principles follow directly from that guidance:

1. **Keep runtime memory smaller than source memory.** The vault can be large; the active context cannot.[cite:36][cite:63]
2. **Prefer structured note-taking over chronological transcript hoarding.** Notes should preserve facts, decisions, and unresolved issues rather than raw history.[cite:36][cite:63]
3. **Compact before overflow.** Memory must be rewritten before the context window is crowded, not after failures begin.[cite:36][cite:63]
4. **Clear re-fetchable detail.** If data can be regenerated from source notes, it does not belong in the always-loaded memory artifact.[cite:63]
5. **Pin only stable, high-value blocks.** Identity, rules, canon, and unresolved critical items deserve persistent placement; verbose history does not.[cite:8][cite:2][cite:36]

## Reference architecture

### High-level model

```text
Obsidian vault (human-friendly source)
  ├─ identity/
  ├─ canon/
  ├─ decisions/
  ├─ open-loops/
  ├─ constraints/
  ├─ examples/
  └─ templates/
        ↓
Metadata queries + templated transforms
        ↓
Compaction / dedup / ranking / expiry filtering
        ↓
Token counting against model-specific budget
        ↓
Compiled runtime artifact (always loaded)
        ↓
System prompt + task + generation headroom
```

This architecture preserves rich editable knowledge upstream while forcing strict discipline at the final compilation step. It separates maintainability concerns from runtime token economics.[cite:36][cite:63][cite:66]

### Source vs runtime responsibilities

| Layer | Purpose | Format | Size expectation | Reads by LLM directly? |
|---|---|---|---|---|
| Obsidian vault | Authoring, organization, history, review | Markdown + frontmatter + links [cite:66][cite:84] | Can be large [cite:66] | No [cite:36] |
| Export intermediates | Query outputs, ranked note sets, summaries | Markdown or JSON [cite:59][cite:81] | Medium [cite:81] | Usually no [cite:63] |
| Final memory artifact | Persistent runtime memory | Compact text or block file [cite:8][cite:63] | Hard-capped [cite:8] | Yes [cite:8] |

## Vault design for specialized agents

Each specialized agent should have either its own vault or a strict namespace inside a shared vault. Isolation is important because one agent’s memory density depends on not carrying another agent’s irrelevant working facts.[cite:36][cite:63]

A practical vault layout looks like this:

```text
agent-vault/
  00_identity/
    agent-profile.md
    mission.md
  01_rules/
    style-rules.md
    hard-constraints.md
  02_canon/
    world-facts.md
    entities/
    taxonomies/
  03_decisions/
    2026-04-29-decision-001.md
    2026-04-30-decision-002.md
  04_open_loops/
    unresolved-issues.md
    pending-questions.md
  05_examples/
    exemplar-outputs.md
  06_summaries/
    rolling-summary.md
    compressed-canon.md
  90_exports/
    ranked-notes.md
    memory.txt
  99_templates/
    decision-template.md
    canon-template.md
```

This structure works because it reflects different memory behaviors. Identity and rules are mostly stable; canon evolves slowly; decisions accumulate and then must be compacted; open loops are volatile and should shrink when resolved.[cite:36][cite:63][cite:8]

## Recommended note schema

A frontmatter schema gives the compiler deterministic handles for selection and compression.[cite:82][cite:84]

| Field | Purpose | Example |
|---|---|---|
| `agent` | Ownership / isolation | `novel-writer` |
| `block` | Target runtime section | `canon`, `rules`, `open_loops`, `recent_decisions` |
| `priority` | Selection weight | `1-10` |
| `stability` | Compression behavior | `core`, `stable`, `volatile` |
| `status` | Lifecycle | `active`, `resolved`, `superseded` |
| `expires` | Time-based pruning | `2026-05-31` |
| `compile` | Whether eligible for export | `true` |
| `source_type` | Provenance | `manual`, `generated`, `validated` |
| `max_lines` | Output bound for note export | `6` |
| `supersedes` | Canon replacement | `decision-017` |

Example note:

```yaml
---
agent: creature-designer
block: canon
priority: 9
stability: stable
status: active
compile: true
source_type: validated
max_lines: 5
---
```

Using frontmatter in this way aligns well with Dataview’s indexing model and enables automated filtering and ranking.[cite:82][cite:84]

## The compiler: the crucial missing layer

The compiler is the part that turns “Obsidian + context engineering” into a usable agent-memory system. Without it, the vault remains too verbose and too irregular for efficient full-load use.[cite:36][cite:63]

### Compiler stages

1. **Query selection:** gather only notes where `compile: true` and `agent` matches the target agent.[cite:82][cite:84]
2. **Resolve supersession:** discard notes marked `superseded`, fold replacements into canonical output, and exclude resolved items.[cite:36][cite:63]
3. **Normalize text:** strip decorative headings, backlinks, verbose prose, and non-runtime commentary.[cite:36]
4. **Rank within blocks:** prefer higher `priority`, more recent unresolved decisions, and validated facts.[cite:36][cite:63]
5. **Compress aggressively:** summarize decision history, merge duplicate canon facts, and turn long notes into terse bullet lines.[cite:36][cite:63]
6. **Measure tokens:** count against the target tokenizer before finalization.[cite:63]
7. **Emit a final memory artifact:** output a deterministic file with fixed block order and hard caps.[cite:8][cite:63]

### Why fixed blocks beat freeform memory

Letta’s “memory blocks” model is powerful because it makes persistent context legible and bounded. Each block is always visible and length-limited, so the system has a natural structure for deciding what belongs where and when something must be compressed.[cite:2][cite:8]

A custom memory compiler should mimic that idea using explicit sections such as:

```text
[IDENTITY]
[OPERATING_RULES]
[CANON]
[ACTIVE_GOALS]
[OPEN_LOOPS]
[RECENT_DECISIONS]
[EXAMPLES]
```

This is better than a single growing markdown note because block boundaries create local budgets and local compaction policies. The model also receives a more interpretable context shape, which helps it know where to look for different kinds of information.[cite:2][cite:8][cite:36]

## Compression strategies for Obsidian-based memory

### Progressive summarization

Progressive summarization means repeatedly rewriting notes into denser forms instead of keeping raw chronological history forever. Anthropic recommends compaction as a first lever for long-horizon tasks, summarizing a context window near its limit into a high-fidelity compressed continuation.[cite:36][cite:63]

Applied to an Obsidian vault, the pattern becomes:

- raw decision notes are captured individually,
- then merged into a rolling summary,
- then stable outcomes migrate into canon,
- while obsolete detail is removed from the runtime artifact.[cite:36][cite:63]

### Decision log rolling windows

Decision logs are useful while a thread is active, but most old decisions should not remain verbatim in always-loaded memory. Instead, the last few unresolved or recently impactful decisions stay in `RECENT_DECISIONS`, while older decisions are folded into `CANON` or archived in the vault.[cite:36][cite:63]

This keeps the runtime artifact focused on “what still matters now” rather than “everything that ever happened.”[cite:36]

### Canon migration

When a decision stops being controversial and becomes settled policy or settled world truth, it should move from decision history into canon. That reduces duplication and shortens the active memory without losing the information.[cite:36][cite:63]

For example:

- decision note: “Use diegetic UI language in all survival-horror prompts.”
- migrated canon line: “Diegetic UI tone is mandatory unless explicitly overridden.”

The migrated canon line is much shorter and more reusable.[cite:36]

### Expiry and staleness pruning

Volatile notes should expire automatically unless reaffirmed. A frontmatter field such as `expires` or `last_validated` allows the compiler to discard temporary assumptions that were never promoted into stable canon.[cite:82][cite:84]

This prevents the memory artifact from filling up with stale hypotheses, abandoned experiments, and solved problems.[cite:36][cite:63]

## Token budget design

Anthropic emphasizes that context is a finite resource with diminishing returns and that models experience “context rot” as windows become crowded.[cite:36] For small local models, the practical implication is that persistent memory must be a minority of the total budget, not the majority.[cite:36][cite:63]

A useful budgeting formula is:

```text
remaining_for_generation = max_context
  - system_prompt
  - persistent_memory
  - active_task
  - recent_messages
  - safety_margin
```

### Suggested 8,192-token allocations

| Agent type | System | Persistent memory | Active task + recent turns | Generation headroom | Notes |
|---|---:|---:|---:|---:|---|
| Novel writer | 900 | 1,800 | 3,400 | 1,600 | More canon and style memory [cite:36][cite:63] |
| Creature designer | 900 | 1,500 | 3,700 | 1,600 | More room for structured specs [cite:36] |
| Unity scene assembler | 1,100 | 1,200 | 4,200 | 1,400 | More live task state, less long canon [cite:36] |
| Research sub-agent | 800 | 1,000 | 4,500 | 1,500 | Most memory should live in notes, not prompt [cite:36][cite:63] |

These are implementation heuristics, not vendor standards. The main point is that persistent memory must be explicitly budgeted and capped like any other prompt component.[cite:36][cite:63]

## Runtime enforcement

A production-grade implementation should enforce limits before every model call.

### Enforcement loop

1. Build the prompt from system instructions, compiled memory, active task, and recent turns.
2. Count tokens with the serving model’s tokenizer or the most faithful available counting method.[cite:63]
3. If the budget is exceeded or safety margin is threatened, compact the largest volatile block first, usually `RECENT_DECISIONS` or `OPEN_LOOPS`.[cite:36][cite:63]
4. Recount and only then send the request.

Letta’s design is instructive here because block length limits are configurable and writes that exceed those limits fail visibly. That makes overgrowth an explicit event instead of a silent prompt-quality failure.[cite:8]

### Practical thresholds

A conservative policy is:

- **Green:** memory artifact under 80 percent of its budget,
- **Yellow:** 80 to 95 percent, queue compaction,
- **Red:** above 95 percent, block write or force immediate compression.

This mirrors the spirit of bounded core memory rather than allowing unbounded drift.[cite:8][cite:63]

## Detailed Obsidian workflow

### Step 1: capture notes in structured templates

Use Templater to create a note for each memory event type.[cite:74][cite:77] Each template should minimize prose and encourage compact fields.

Example decision template:

```markdown
---
agent: novel-writer
block: recent_decisions
priority: 8
stability: volatile
status: active
compile: true
---
# Decision
- Issue: 
- Chosen option: 
- Why: 
- Affects: 
- Promote to canon when: 
```

### Step 2: query notes by block

Use Dataview to collect candidate notes for each runtime section based on metadata.[cite:82][cite:84]

Example idea:

```dataview
TABLE block, priority, status
FROM "03_decisions"
WHERE agent = "novel-writer" AND compile = true AND status = "active"
SORT priority DESC
```

### Step 3: write deterministic export notes

Use Dataview + Templater or Run to write plain Markdown export files into `90_exports/`.[cite:81][cite:59] These exports should already be simplified and ranked, so the external compiler has less work to do.[cite:81][cite:59]

### Step 4: external compile pass

A CLI tool should then convert those export notes into the final runtime artifact. This pass should remove redundant labels, flatten text, trim examples, merge duplicates, enforce caps, and produce a predictable block order.[cite:36][cite:63]

### Step 5: validate and commit

If token counts pass, write the artifact and commit the vault changes with Git. If they fail, produce a report listing which blocks exceeded their limits and which notes were dropped or compressed.[cite:75][cite:72][cite:63]

## Success cases and implemented patterns

### 1. Claude Code: persistent files + compaction + memory

Anthropic describes Claude Code as using persistent `CLAUDE.md` files for user-defined rules and workflow guidance, while also layering compaction and memory techniques for long-running agent sessions.[cite:63][cite:36] This is one of the clearest production-grade examples of “always-load some stable memory, compress the rest, and keep the context window lean.”[cite:63][cite:36]

Why this matters for Obsidian:

- `CLAUDE.md` is conceptually similar to a compiled memory artifact.[cite:63]
- The editable source could live in Obsidian, then be compiled into that stable file.[cite:66][cite:81]
- Compaction and tool-result clearing prove that raw history should not remain permanently in prompt context.[cite:63]

### 2. Claude Plays Pokémon: external notes preserve long-horizon coherence

Anthropic reports that Claude playing Pokémon maintained notes about maps, achievements, training progress, and combat strategies across context resets, allowing the agent to continue multi-hour trajectories after summarization steps.[cite:36] This is a concrete implemented success case of structured note-taking enabling continuity that would not fit in raw context alone.[cite:36][cite:63]

Why this matters for Obsidian:

- the vault can hold the durable notes,
- the runtime artifact can load only the current distilled state,
- and resets become survivable because the agent is not dependent on full message history.[cite:36][cite:63]

### 3. Letta core memory: bounded pinned blocks

Letta’s memory blocks are always visible in context, labeled, and length-limited by design.[cite:2][cite:8] This is an implemented product pattern proving that persistent always-loaded memory is viable when it is bounded, structured, and block-oriented rather than treated as an ever-growing freeform note.[cite:2][cite:8]

Why this matters for Obsidian:

- Obsidian can author richer source notes,
- but the final output should imitate Letta-style pinned blocks,
- not an unbounded notebook dump.[cite:2][cite:8]

### 4. Obsidian automation patterns: query, render, export

Dataview provides metadata querying over Markdown notes, Templater provides scripted note generation and transformation, and community patterns show that Dataview query results can be written back into plain Markdown files for export workflows.[cite:82][cite:84][cite:81] The Run plugin similarly supports generated Markdown from Dataview and JavaScript.[cite:59]

This is not a turnkey agent-memory product by itself, but it is a successfully implemented tooling pattern that makes Obsidian practical as the source layer for compiled memory systems.[cite:59][cite:81]

## Benefits of the Obsidian + context-engineering approach

### Major strengths

- **Offline and local-first:** vault data lives in local Markdown files.[cite:66][cite:67]
- **Inspectable:** every source note and every compaction output can be reviewed directly.[cite:66][cite:75]
- **Git-friendly:** changes to memory are auditable and reversible.[cite:75][cite:72]
- **Metadata-rich:** frontmatter gives deterministic control over selection and compression.[cite:84][cite:82]
- **Human-friendly:** non-engineering collaborators can review or edit notes more easily than database rows.[cite:66][cite:67]
- **Runtime-agnostic:** the final artifact can be consumed by llama.cpp, Ollama-based stacks, or custom local runtimes because it is just text.[cite:66][cite:63]

### Strategic advantage

This pattern avoids two common failures at once:

1. It avoids opaque memory black boxes where the model’s persistent state is hard to inspect.[cite:63]
2. It avoids naive “just load all the notes” behavior that wastes tokens and degrades model focus.[cite:36]

## Risks and failure modes

### Mistaking the vault for the prompt

The biggest mistake is loading raw Obsidian notes into context as-is. Obsidian notes often contain headings, backlinks, commentary, duplicated facts, and prose written for humans rather than models.[cite:66][cite:67]

### Plugin dependency sprawl

A second risk is overbuilding inside Obsidian itself. Dataview, Templater, Run, and Git are useful, but the core compiler should still exist outside the vault so that runtime correctness does not depend on Obsidian being open.[cite:59][cite:75][cite:81]

### Weak compaction rules

If compaction is too vague, runtime memory becomes a bloated diary. If compaction is too aggressive, the system loses subtle but critical context. Anthropic explicitly notes this balance in compaction design and recommends tuning for recall first, then improving precision.[cite:36]

### Metadata drift

If note schemas are not enforced, export quality degrades quickly. That is why templates, required fields, and validation rules are essential.[cite:74][cite:77][cite:84]

## Best-practice implementation blueprint

### Recommended runtime blocks

| Block | Purpose | Suggested policy |
|---|---|---|
| `IDENTITY` | Agent role, scope, core objectives | Mostly static; rewrite rarely |
| `OPERATING_RULES` | Hard rules, stylistic constraints, forbidden actions | Static; highest priority |
| `CANON` | Stable world facts, accepted domain truths, standards | Merge duplicates; promote validated decisions here |
| `ACTIVE_GOALS` | Current milestone or deliverable targets | Replace often; keep short |
| `OPEN_LOOPS` | Unresolved questions, blockers, unknowns | Remove immediately when resolved |
| `RECENT_DECISIONS` | Only the last few consequential decisions | Rolling window; compact first |
| `EXAMPLES` | Minimal canonical examples | Keep tiny; drop if not mission-critical |

This block strategy closely matches the lessons from bounded core memory systems and compaction-oriented agent design.[cite:8][cite:2][cite:36]

### Recommended compaction policies by block

| Block | Compression style | Trigger |
|---|---|---|
| `IDENTITY` | Manual rewrite only | Rare |
| `OPERATING_RULES` | Manual or validated rewrite | On policy change |
| `CANON` | Deduplicate + merge | On every build |
| `ACTIVE_GOALS` | Replace full block | New milestone |
| `OPEN_LOOPS` | Delete resolved lines; merge duplicates | Any status change |
| `RECENT_DECISIONS` | Summarize older items into canon or one-line history | Budget pressure |
| `EXAMPLES` | Keep 1-3 only | Budget pressure |

## A concrete operating model

A mature implementation should use the following loop:

1. Create or update source notes in Obsidian through templates.[cite:74][cite:77]
2. Query and materialize candidate exports via Dataview and scripted generation.[cite:82][cite:81][cite:59]
3. Run an external compiler to generate `memory.txt` with fixed blocks.[cite:36][cite:63]
4. Count tokens before inference and refuse over-budget outputs.[cite:63][cite:8]
5. On threshold breach, compact volatile blocks and re-run the build.[cite:36][cite:63]
6. Commit both source and compiled artifacts with Git for traceability.[cite:75][cite:72]

## Recommended stack

| Component | Recommendation | Why |
|---|---|---|
| Authoring | Obsidian vault | Local Markdown, flexible knowledge work [cite:66][cite:67] |
| Metadata/query | Dataview | Frontmatter and query API over notes [cite:82][cite:84] |
| Templates | Templater | Enforces schemas and automation [cite:74][cite:77] |
| Derived exports | Dataview + Run or Templater scripts | Deterministic plain Markdown outputs [cite:81][cite:59] |
| Version control | Obsidian Git or regular Git CLI | Auditable compaction and rollback [cite:75][cite:72] |
| Runtime memory model | Letta-style labeled blocks | Pinned, bounded, interpretable memory [cite:2][cite:8] |
| Long-horizon control | Anthropic-style compaction + note-taking | Prevents context bloat [cite:36][cite:63] |

## Final assessment

Obsidian + context engineering is a strong architecture for specialized local agents **if and only if** it is implemented as a source-to-runtime compilation pipeline rather than a direct-note-loading workflow.[cite:36][cite:63][cite:66] It combines human-friendly knowledge management with disciplined prompt economics, and it maps well to local/offline development practices because everything can remain file-based, inspectable, and Git-controlled.[cite:66][cite:75][cite:72]

The most important design rule is simple: the vault is the workshop, not the working memory. The vault can be rich, verbose, and historically complete; the runtime artifact must be sparse, structured, bounded, and relentlessly pruned.[cite:36][cite:63][cite:8]

For teams building persistent specialized agents under small local context windows, this is one of the most promising patterns available because it combines three proven ideas:

- local file-backed notes,[cite:66][cite:67]
- context compaction and structured memory,[cite:36][cite:63]
- and bounded pinned memory blocks.[cite:2][cite:8]

## Recommended next step

The next engineering step should be a concrete specification for:

1. the Obsidian frontmatter schema,
2. the compiler rules,
3. the block budget limits,
4. the token-count validation step,
5. and the exact shape of the final `memory.txt` artifact.

That specification should be written before implementation so the vault structure, note templates, and runtime loader all evolve around the same memory contract.[cite:74][cite:82][cite:63]
