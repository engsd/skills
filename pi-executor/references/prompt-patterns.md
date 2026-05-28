# Prompt Patterns

Use short, bounded prompts. Pi is the executor.

## New implementation step

```text
Goal:
Implement [specific change].

Context:
- Workspace: [path]
- Focus area: [file/module/feature]
- Code modification is allowed.

Requirements:
1. Make the change directly.
2. Keep the change scoped.
3. Report what changed and any blocker.

Return:
- files changed
- summary
- blocker if any
```

## Debugging step

```text
Goal:
Diagnose and fix [specific failure].

Context:
- Workspace: [path]
- Relevant command or error: [details]

Requirements:
1. Identify the most likely cause.
2. Apply the smallest reasonable fix.
3. Report the exact fix and remaining risk.
```

## Writing step

```text
Goal:
Write or revise [document/artifact].

Context:
- Workspace: [path]
- Target file or output: [path/name]
- Writing is the primary task.

Requirements:
1. Produce the draft directly.
2. Keep style aligned to the request.
3. Report what was written.
```

## Recovery step after intervention

```text
Previous attempts hit a blocker.

New direction:
- The blocker was: [summary]
- Do not repeat: [failed path]
- Now do: [new narrow task]

Return:
- result
- files changed
- next blocker if unresolved
```
