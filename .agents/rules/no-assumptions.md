# 🔒 INVIOLABLE: No Assumptions — Evidence Required Before Action

**Priority**: CRITICAL | **Applies To**: ALL work — debugging, deployments, code changes, DB operations, model evaluation, metric scoring

---

## 🚨 THE RULE

**NEVER act on an assumption. NEVER use "probably" as justification to change anything.**

Before modifying ANY file, running ANY command, or applying ANY fix:

1. **GET THE REAL DATA** — read the actual log, the actual stack trace, the actual HTTP response body, the actual raw model output
2. **STATE THE EVIDENCE** — quote the exact error message, the exact metric value, the exact raw output
3. **FORM A HYPOTHESIS** — state it explicitly: "The error is X because the log says Y"
4. **VERIFY THE HYPOTHESIS** — run a read-only check that confirms the root cause before fixing
5. **ONLY THEN FIX** — apply the minimal fix that addresses the confirmed root cause

---

## ❌ FORBIDDEN

```
❌ "probably the issue is..."
❌ "this might be caused by..."
❌ "it seems like..."
❌ "I think the error is..."
❌ Applying a fix because something "looks related"
❌ Granting DB permissions before reading the exact error
❌ Modifying code before reading the actual stack trace
❌ Assuming a fix worked without verifying via logs/output
❌ Interpreting a metric score without reading the raw data that produced it
❌ Concluding a model "fails" based on aggregate scores without seeing actual model output
❌ Concluding a scorer "has a bug" without testing it on known inputs first
❌ Running a second test suite without understanding why the first one produced the results it did
❌ Changing a test, prompt, or scorer because the score "looks wrong" without reading the raw output
❌ Launching parallel operations that make it impossible to isolate which step caused a problem
❌ Saying "the results suggest X" without quoting the exact data point that leads to X
```

---

## ✅ REQUIRED WORKFLOW FOR EVERY BUG/ERROR

```
Step 1: READ the actual raw data
  → Logs, HTTP response bodies, stack traces, DB error messages
  → For model evaluation: the actual model output text, not just the score
  → Quote the EXACT content — do not paraphrase or summarize

Step 2: IDENTIFY the root cause from evidence
  → "The log at [timestamp] shows: [exact error text]"
  → "The model output for run 1 was: [exact text]"
  → "This is caused by: [specific file:line or exact behavior]"

Step 3: VERIFY before acting
  → Run a read-only check to confirm the cause
  → e.g. check DB grants BEFORE applying grants
  → e.g. check what file/function throws BEFORE editing it
  → e.g. test the scorer on known inputs BEFORE concluding it has a bug
  → e.g. read the raw model output BEFORE concluding the model failed

Step 4: APPLY the minimal fix
  → One fix per confirmed root cause
  → After applying: verify via logs/response that the fix worked

Step 5: CONFIRM with evidence
  → Show the log/response that proves the fix worked
  → Do NOT say "it should work now" without proof
```

---

## 📊 SPECIFIC RULES FOR MODEL EVALUATION

When evaluating LLM outputs via automated scorers:

```
MANDATORY: Every test run MUST save the raw model output alongside the score.
MANDATORY: Before concluding a model "fails" a test, read at least 2 raw outputs.
MANDATORY: Before concluding a scorer "has a bug", test it on 3 hand-crafted known inputs.
MANDATORY: Score=0 does NOT mean "output was empty" — read the actual output first.
MANDATORY: Aggregate metrics (avg, pass@5) are summaries — always trace back to raw runs.

FORBIDDEN: Rewriting prompts based on score alone without reading what the model generated.
FORBIDDEN: Declaring a test invalid without running it against a known-good output.
FORBIDDEN: Changing the scorer without evidence that the current scorer produced wrong results.
```

---

## ⚙️ SPECIFIC RULES FOR SERVER/SYSTEMD OPERATIONS

```
MANDATORY: Before applying any fix to a service file, run the binary directly from terminal first.
MANDATORY: Read the exact journalctl error line before changing ANY parameter.
MANDATORY: Test one change at a time — never change format + flags simultaneously.
MANDATORY: Confirm the service is actually stopped before re-deploying.

FORBIDDEN: Making parallel changes to a service file and environment simultaneously.
FORBIDDEN: Launching background downloads while also debugging a service failure.
FORBIDDEN: Assuming a restart loop is caused by a specific parameter without checking the log.
```

---

## Example of WRONG behavior (never do this)

```
❌ Score=0 seen → "probably a scorer bug" → rewrite scorer → run again → still 0 → guess again

❌ Service fails → "probably systemd escaping issue" → change format → still fails
                → "probably needs EnvironmentFile" → change again → still fails
                → (never read the actual binary error first)

❌ Model scores low → "probably the prompt is wrong" → rewrite prompt → run again
                   → (never read what the model actually output)
```

## Example of CORRECT behavior

```
✅ Score=0 seen
   → Read raw model output for run 1: model responded in English, ignored char_elena ID
   → Read raw model output for run 2: same — model rephrased prompt in own words
   → Test scorer on known input with char_elena: scorer returns 3 entities ✓
   → Hypothesis confirmed: model ignores ID-format entities, scorer is correct
   → Fix: update prompt to make ID usage explicit, or accept as model limitation
   → Verify: rerun 3 times, check raw output includes char_elena in at least 2/3

✅ Service fails
   → journalctl shows: "parse error... invalid literal; last read: '{e'"
   → Run binary directly: ~/llama-server --chat-template-kwargs '{"enable_thinking":false}'
   → Binary works → confirms systemd quoting strips the quotes
   → Fix: use EnvironmentFile with the raw value
   → Verify: systemctl status shows active (running), curl /health returns 200
```

---

**Version**: 2.0 | **Created**: Apr 27, 2026 | **Updated**: May 1, 2026
**Changes v2.0**: Added model evaluation rules, server/systemd rules, parallel operation restrictions, raw data mandate
