# Pi Command Protocol

Use the global wrapper:

```powershell
& 'C:\Users\eng\ps1\pi.ps1' <action> ...
```

## Session selection order

Use this exact order:

1. `-SessionId`
2. `-Alias`
3. default workspace session
4. create a new session with `start`

## Actions

### `start`

Use when beginning a new Pi task.

Recommended pattern:

```powershell
& 'C:\Users\eng\ps1\pi.ps1' start -Workspace 'C:\path\to\project' -Alias 'task-name' -Prompt 'Do X'
```

### `send`

Use when continuing an existing task.

Recommended pattern:

```powershell
& 'C:\Users\eng\ps1\pi.ps1' send -Workspace 'C:\path\to\project' -Prompt 'Continue with Y'
```

### `use`

Use when you want to bind a specific session as the default workspace session.

### `status`

Use to inspect the currently bound default session.

### `list`

Use to inspect known sessions for a workspace before choosing one.

### `show`

Use when you need details for one session.

### `fork`

Use when you want a new session that inherits context from an existing one but should diverge.

### `raw`

Use only when the standard actions do not cover the need. Prefer the structured actions first.

## Workspace rules

- If the shell is already in the target project, `-Workspace` is optional.
- If there is any ambiguity, pass `-Workspace` explicitly.
- For cross-project work, always pass `-Workspace`.

## Output handling

Use `-Json` when structured parsing helps the current AI decide the next step.

Prefer plain text when simply reading Pi's answer is enough.
