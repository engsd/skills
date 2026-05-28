---
name: pi-executor
description: Use Pi as the execution worker for real project work across any directory. Trigger when the user wants AI to carry out coding, writing, debugging, refactoring, or multi-step project work through Pi with session continuity, while the current AI stays responsible for planning, supervision, fallback, and verification.
---

# Pi Executor

Use this skill when the user wants the current AI to work through Pi rather than only answering directly.

Keep the description narrow in your own head: this skill is for **delegating real execution to Pi**. Do not trigger it for normal Q&A, lightweight explanation, or situations where Pi adds no value.

## Operating model

Run a two-layer workflow:

- **Decision AI**: the current assistant. Owns intent capture, task shaping, session choice, supervision, verification, escalation, and final reporting.
- **Pi**: the execution worker. Owns writing code, writing docs, editing files, reading projects, and running project commands.

Pi is not the final authority. Treat Pi outputs as execution reports that must be checked.

## When to use

Use this skill when one or more of these are true:

- The user wants AI to use Pi directly.
- The task is multi-step and benefits from a persistent Pi session.
- The task requires real project work in any directory: coding, refactoring, debugging, implementation, writing, or project analysis.
- The task should continue across turns and you want a stable worker session.

Do not use this skill for:

- simple factual answers
- short code explanation with no execution
- cases where direct local work by the current AI is simpler and clearly better

## Pi entrypoint

Always use the global Pi wrapper:

```powershell
C:\Users\eng\ps1\pi.ps1
```

Use `-Workspace <path>` whenever the target project is not the current shell directory, or when you want to be explicit.

## Default workflow

### 1. Ground the task

Before calling Pi, determine:

- target workspace
- whether this is a new task or a continuation
- whether the user specified a session id or alias
- whether code modification is allowed
- what completion for this step looks like

Infer these from context whenever safely possible.

### 2. Choose the session

Use this priority order:

1. explicit `-SessionId`
2. explicit `-Alias`
3. default bound session for that workspace
4. if no session exists, create one with `start -Alias <name>`

Default behaviors:

- For a new task, prefer `start -Alias <task-name>`.
- For ongoing work, prefer `send`.
- Do not `reset` unless there is a concrete reason.
- Do not delete Pi session files.

### 3. Give Pi bounded work

Send Pi one clear step at a time. Pi should do the concrete writing or coding work.

Your Pi prompt should include:

- goal
- workspace context if relevant
- file or subsystem focus
- whether modification is allowed
- expected output shape
- stop condition for the current step

Keep prompts direct. Pi is the worker, not the planner.

## Decision AI responsibilities

The current AI must:

- decide when Pi should be used
- decide which workspace and session to use
- frame the task into an executable step
- inspect Pi output before trusting it
- decide whether to continue, adjust, or intervene
- report progress back to the user clearly

When Pi completes a step, verify the result locally when possible.

## Escalation policy

Intervene immediately when:

- Pi hits a permission problem
- Pi drifts away from the requested goal
- Pi reports success but the local result does not support that claim

Intervene after repeated failure when:

- the same problem has been retried 5 times and is still unresolved

When intervening:

1. summarize the issue
2. identify what Pi has already tried
3. decide whether to fix the environment, change the prompt, switch sessions, or solve the issue directly
4. if Pi should continue, give it a new explicit instruction

Do not let Pi loop indefinitely on the same failure.

## Permissions and safety

Pi is allowed to modify code and documents when the task calls for it.

Still enforce these boundaries:

- obey the user's deletion rules
- avoid destructive cleanup unless explicitly confirmed
- do not reset or destroy sessions casually
- do not assume Pi-authored output is correct without review

## Verification checklist

After each meaningful Pi step, check the relevant items:

- correct workspace
- correct session
- output matches the requested task
- code or docs were actually updated where expected
- command output supports Pi's conclusion
- no obvious silent failure or partial completion

## Command guide

Common commands:

```powershell
# start a new worker session
& 'C:\Users\eng\ps1\pi.ps1' start -Workspace 'C:\path\to\project' -Alias 'task-name' -Prompt 'Your task'

# continue the default session
& 'C:\Users\eng\ps1\pi.ps1' send -Workspace 'C:\path\to\project' -Prompt 'Next step'

# continue a specific session
& 'C:\Users\eng\ps1\pi.ps1' send -Workspace 'C:\path\to\project' -SessionId '...' -Prompt 'Next step'

# inspect session state
& 'C:\Users\eng\ps1\pi.ps1' status -Workspace 'C:\path\to\project'
& 'C:\Users\eng\ps1\pi.ps1' list -Workspace 'C:\path\to\project'
```

## References

Read only what you need:

- `references/pi-command-protocol.md` for command selection and session rules
- `references/escalation-policy.md` for intervention and retry handling
- `references/prompt-patterns.md` for prompt templates to Pi
- `references/workspace-session-examples.md` for common usage examples
