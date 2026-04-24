# SPEC: Context-Engineering Agent with Persistent Memory
> Pattern: Stateful conversational agent using file-based memory
> Input: Chat history + existing context files
> Output: A fully operational agent that resumes any session with full context
> Domain: Agnostic — applies to any specialization

---

## 1. Problem Statement

LLM sessions are stateless by default. Every new conversation starts from zero. For long-running projects (weeks or months), this means:
- Repeating context in every session
- Decisions get forgotten or contradicted
- No single source of truth for project state
- The user carries all the cognitive load of continuity

**Goal:** Build an agent that remembers everything across sessions — decisions, artifacts, stakeholders, conventions, current state — without the user having to re-explain it.

---

## 2. Core Architecture

The system has four components:

```
┌─────────────────────────────────────────────────────┐
│                    AGENT RUNTIME                    │
│                                                     │
│  CLAUDE.md          ← Identity + rules + protocols  │
│  context/           ← Persistent memory files       │
│  .claude/commands/  ← Skills (/context-start, etc.) │
│  inputs/            ← Raw source documents          │
│  outputs/           ← Generated artifacts           │
└─────────────────────────────────────────────────────┘
```

### Component 1 — CLAUDE.md (Agent Identity)
The single file that defines WHO the agent is, WHAT it does, and HOW it behaves. Loaded automatically by Claude Code at every session start.

### Component 2 — context/ (Memory Layer)
Four markdown files that together form the agent's persistent memory. Updated at session close, loaded at session start.

### Component 3 — Skills (Session Lifecycle)
Two slash commands that automate memory load/save: `/context-start` and `/context-close`.

### Component 4 — inputs/ and outputs/
Source documents the agent reads from, and artifacts it produces. Never modified by the agent except `outputs/`.

---

## 3. Required File Structure

```
project-root/
├── CLAUDE.md                          ← Agent identity (required)
├── context/
│   ├── project_state.md               ← Who, what, why, stakeholders
│   ├── artifacts_registry.md          ← All artifacts and their status
│   ├── conversation_memory.md         ← Compressed decision history
│   └── next_steps.md                  ← Current state + next actions
├── .claude/
│   └── commands/
│       ├── context-start.md           ← Session open skill
│       └── context-close.md           ← Session close skill
├── inputs/                            ← Source documents (read-only)
├── outputs/                           ← Generated artifacts
└── scripts/                           ← Optional automation scripts
```

---

## 4. CLAUDE.md — Specification

Must contain these sections:

### 4.1 `/agent.role`
Defines the agent's identity, purpose, and what project it belongs to. Written in second person ("You are…"). Should answer:
- What is this project?
- What is the agent's function?
- What does the agent know?
- Where does context live?

### 4.2 `/protocols.operational`
Numbered list of hard rules the agent must follow in every session. Examples:
- Language to respond in
- Unit of analysis (e.g., "always refer to X as Y")
- What to check before generating documents
- Who to coordinate with for what
- Scope constraints

### 4.3 `/memory.load`
Explicit ordered instruction to load context files at session start:
```
1. context/project_state.md
2. context/artifacts_registry.md
3. context/conversation_memory.md
4. context/next_steps.md
```

### 4.4 `/docs.policy`
Rules about read-only folders, historical files, and what should never be modified.

---

## 5. Memory Files — Specification

### 5.1 `context/project_state.md`
**Purpose:** Stable reference. Changes rarely.
**Contains:**
- Project name, client, team, timeline
- Strategic objective (why does this project exist?)
- Organizational hierarchy relevant to the work
- Team roster with roles and responsibilities
- Stakeholder map with names, roles, and critical notes
- Active risks and alerts
- Methodological frameworks in use
- Key glossary

**Update trigger:** Only when team, scope, or methodology changes.

### 5.2 `context/artifacts_registry.md`
**Purpose:** Single source of truth for all produced files.
**Contains per artifact:**
- File path (exact)
- Status: ✅ Active / 🔒 Historical / 🔧 In progress
- Date generated or last modified
- Structure description (sheets, columns, sections)
- Key decisions embedded in the artifact
- Conventions that must be preserved

**Update trigger:** Every time a file is created, modified, or deprecated.

### 5.3 `context/conversation_memory.md`
**Purpose:** Compressed history of decisions and evolution.
**Contains:**
- Timeline of key decisions (grouped by date)
- For each decision: context → options considered → decision taken → why
- Evolution of artifacts (what changed and why)
- Stakeholder interactions that changed direction
- Discarded approaches and the reason they were discarded

**Format:** Chronological, compressed. Not a transcript — a decision log.

**Update trigger:** After every session where a meaningful decision was made.

### 5.4 `context/next_steps.md`
**Purpose:** Operational handoff file. Most frequently updated.
**Contains:**
- Current phase/stage
- Active source file (if applicable)
- ✅ Completed in last session (with file paths)
- 🔴 Urgent pending items
- 🟡 In-progress items
- ⬜ Queued next actions
- Critical technical context for the next session (exact rules, known gotchas)
- Questions to ask the user at session start

**Update trigger:** Every session close.

---

## 6. Skills — Specification

### 6.1 `/context-start`
**File:** `.claude/commands/context-start.md`

**Behavior:**
1. Load the 4 memory files in order
2. Present structured welcome summary:
   - Current project phase
   - Last artifact generated (file, date)
   - Top 3–5 active design decisions
   - Pending items (urgent / in-progress / next)
3. Ask the user what to work on today

**Template structure for the summary:**
```
### Project status
### Active decisions
### Pending items (🔴 🟡 ⬜)
### What are we working on today?
```

### 6.2 `/context-close`
**File:** `.claude/commands/context-close.md`

**Behavior:**
1. Summarize what was accomplished in this session
2. Update `context/next_steps.md` — mark completed, add new pending
3. Append new decisions to `context/conversation_memory.md`
4. Update `context/artifacts_registry.md` for any new/modified files
5. Confirm all files saved
6. Print closing summary

---

## 7. Bootstrap Process (Building the Agent from Existing Chat History)

When creating a context-engineering agent from an existing project with chat history:

### Step 1 — Extract raw chat
Export or copy the full conversation to `inputs/chat.txt` (or equivalent).

### Step 2 — Generate `project_state.md`
Read the full chat. Identify and extract:
- Who are the people involved (names, roles, relationships)?
- What is the project about?
- What frameworks or methodologies are used?
- What is the organizational structure?
- What are the active risks?
- Build the glossary from recurring domain-specific terms.

### Step 3 — Generate `conversation_memory.md`
Read the full chat chronologically. For each meaningful decision:
- What was the context/trigger?
- What options were discussed?
- What was decided?
- What was explicitly discarded and why?
Group by date. Compress aggressively — capture the WHY, not the dialogue.

### Step 4 — Generate `artifacts_registry.md`
List every file produced during the conversation:
- Exact path
- What it contains
- Its current status (active / historical / superseded)
- Which version is the source of truth

### Step 5 — Generate `next_steps.md`
Identify the last point of the conversation:
- What was the last thing completed?
- What was left pending?
- What were the open questions?
- Are there technical constraints mentioned for next work?

### Step 6 — Write `CLAUDE.md`
Synthesize steps 2–5 into the agent identity file. Define:
- Agent role (using the project context from step 2)
- Operational protocols (from recurring conventions in the chat)
- Memory load order (always the same 4 files)
- Docs policy (what is read-only, what is historical)

### Step 7 — Write the skills
Create `/context-start` and `/context-close` as `.claude/commands/` files following the spec in §6.

### Step 8 — Validate
Run `/context-start` in a new Claude Code session. The agent should:
- Load context without errors
- Present an accurate project summary
- Know the last artifact generated
- Know the active decisions
- Know what is pending

---

## 8. Design Principles

### 8.1 Memory is files, not prompts
Never rely on "Claude will remember" from the conversation. All memory lives in markdown files that are explicitly loaded. If it's not in a file, it doesn't exist in the next session.

### 8.2 Separate stable from volatile memory
- `project_state.md` = stable (changes rarely)
- `next_steps.md` = volatile (changes every session)
Mixing them makes both harder to maintain.

### 8.3 Compress decisions, not conversations
`conversation_memory.md` should capture decisions and their rationale, not dialogue. A 5-hour conversation should compress to 1–2 pages of decisions. The goal is signal, not transcript.

### 8.4 Artifacts registry is the contract
Every file the agent produces must be registered. The registry prevents the agent from producing contradictory versions, forgetting what exists, or overwriting active work.

### 8.5 Context-close is not optional
The value of the system degrades if `/context-close` is skipped. Make it a habit — every session ends with a close.

### 8.6 CLAUDE.md overrides everything
Instructions in CLAUDE.md take precedence over any default model behavior. Use it to enforce conventions that must never be broken (language, terminology, scope, prohibited actions).

---

## 9. Scaling and Extension Patterns

### Adding domain-specific intel files
For large projects with reference data (e.g., vendor lists, KPI tables, system inventories), create dedicated intel files in `context/`:
```
context/intel_[topic].md
```
Register them in `artifacts_registry.md` and reference them in CLAUDE.md under `/memory.load` as optional secondary loads.

### Adding domain-specific skills
Beyond context-start/close, create skills for recurring domain tasks:
```
.claude/commands/[task-name].md
```
Each skill should: verify dependencies → execute task → validate output → update memory.

### Multi-session audit trail
For projects requiring traceability, add a `context/session_log.md` that appends a one-line entry per session:
```
YYYY-MM-DD | Worked on: [topic] | Artifacts: [files] | Decisions: [count]
```

---

## 10. Anti-Patterns to Avoid

| Anti-pattern | Problem | Fix |
|---|---|---|
| Storing memory in the conversation | Lost on session reset | Move to context/ files |
| One giant context file | Hard to update, slow to load | Split into the 4 dedicated files |
| Vague artifact status | Agent doesn't know what's current | Always mark ✅ Active vs 🔒 Historical |
| Skipping context-close | Memory drifts from reality | Enforce as session ritual |
| Modifying inputs/ | Breaks reproducibility | inputs/ is always read-only |
| Using etree for XML in Excel scripts | Corrupts mc:AlternateContent | String manipulation only |
| Generating files without registering them | Orphan artifacts | Always update artifacts_registry.md |

---

## 11. Minimum Viable Agent Checklist

Before declaring the agent operational:

- [ ] `CLAUDE.md` exists with all 4 sections (role, protocols, memory.load, docs.policy)
- [ ] All 4 context files exist and are populated
- [ ] `/context-start` skill loads files and produces a coherent summary
- [ ] `/context-close` skill updates all relevant memory files
- [ ] `artifacts_registry.md` reflects the current state of all outputs
- [ ] A new Claude Code session using `/context-start` requires no manual re-briefing
- [ ] The agent refuses to contradict registered active artifacts without being explicitly asked to update them

---

*Pattern based on: davidkimai/Context-Engineering framework*
*Implemented and validated on: Claude Code (Anthropic) + Claude Sonnet 4.6*
