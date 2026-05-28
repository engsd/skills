---
name: claude-flow
description: Coordinate long-running work by using Claude Code as the implementation worker while the current AI remains the planner, permission gate, supervisor, and final verifier. Use this skill whenever the user wants Codex/AI to call Claude Code, delegate work to Claude Code, use Claude Code's MCP tools or skills such as n8n MCP, image-workflow, html-anything, Playwright, Cloudinary, Supabase, or run a multi-step workflow where Claude Code executes and the AI monitors, confirms details with the user, handles interruptions, and verifies outputs.
---

# Claude Flow

## English Execution Instructions

Use this skill to run a two-agent operating model:

- **Decision AI**: the current assistant. It owns intent capture, user confirmation, permission gating, prompt design, supervision, verification, and final reporting.
- **Claude Code**: the implementation worker. It owns concrete execution inside Claude Code: using Claude-specific skills, MCP tools, filesystem tools, browser checks, and long-running workflows.

The user should only need to provide a target. The Decision AI should ask one concise confirmation round for missing task details, then drive Claude Code until the task is complete or a real blocker appears.

### 1. When To Use

Use Claude Flow when any of these are true:

- The user asks to "call Claude Code", "let Claude do it", "use Claude's n8n MCP", "use Claude's skills", or "act as supervisor".
- The current assistant cannot directly access a tool that Claude Code can access, especially n8n MCP.
- A workflow is long-running, multi-stage, or benefits from a worker/supervisor split.
- The task involves Claude Code skills under `C:\Users\eng\.claude\skills`, such as `image-workflow`, `html-anything`, `n8n-skills`, `playwright-cli`, `obsidian-*`, or `web-video-presentation`.

### 2. Known Claude Code Environment

Use this local Claude Code entrypoint:

```powershell
C:\Users\eng\.local\bin\claude.exe
```

Use these settings unless the user asks otherwise:

```powershell
C:\Users\eng\.claude\settings.local.json
```

Important observed capabilities:

- Claude Code is configured with `defaultMode: bypassPermissions`.
- Claude Code settings deny destructive delete commands such as `rm` and `rmdir`.
- Installed plugins include GitHub, Cloudflare, Supabase, and Cloudinary.
- Enabled plugins in local settings include Cloudflare, Supabase, and Cloudinary.
- Available Claude skills include `image-workflow`, `html-anything`, `n8n-skills`, `playwright-cli`, `obsidian-cli`, `obsidian-markdown`, `mcp-builder`, `humanizer`, and related skills.
- Claude Code has successfully seen and called n8n MCP tools in this environment, including `n8n_health_check` and `n8n_list_workflows`. Still verify availability at the start of each n8n task.

Never copy secret values from settings into prompts or user-facing answers. Refer to secrets only by capability, such as "Cloudinary credentials are configured".

### 3. Correct Claude Code Interaction Pattern

Use `--print` for controlled one-shot turns. This is not an interactive terminal. It is a persistent one-question/one-answer exchange when paired with a session id.

Start a new persistent conversation with a valid UUID:

```powershell
$sessionId = '33333333-4444-4555-8666-777777777777'
$prompt = @'
Your task prompt here.
'@
& 'C:\Users\eng\.local\bin\claude.exe' --settings 'C:\Users\eng\.claude\settings.local.json' --print --output-format text --allow-dangerously-skip-permissions --permission-mode bypassPermissions --session-id $sessionId -- $prompt
```

Continue the same conversation:

```powershell
$sessionId = '33333333-4444-4555-8666-777777777777'
$prompt = @'
Follow-up prompt here.
'@
& 'C:\Users\eng\.local\bin\claude.exe' --settings 'C:\Users\eng\.claude\settings.local.json' --print --output-format text --allow-dangerously-skip-permissions --permission-mode bypassPermissions --resume $sessionId -- $prompt
```

If `--resume` reports "No conversation found", create the session with `--session-id` and continue. If `--resume` reports the value is not a valid session id, use a valid UUID.

Do not rely on `/skill ...` slash commands. In `--print` mode, `/skill` may return `Unknown command`. Trigger Claude skills with `@skill-name` and natural language, for example:

```text
@image-workflow
Process this Markdown file...
```

### 4. Decision AI Responsibilities

Before delegating, clarify the user's target and define success:

- Input path(s), URL(s), workflow id(s), or desired system.
- Output location and naming rules.
- Whether source files may be modified or only copied.
- Whether generated files may overwrite existing files. Default to safe rename.
- Whether any destructive action is allowed. Default to no deletion.
- Required tools or skills, if any.

Ask the user only for details that are necessary and cannot be inferred safely. After that, drive the workflow without repeatedly asking.

During execution:

- Give Claude Code one bounded task per turn.
- Include constraints in every Claude Code prompt: no deletion, safe rename, output paths, stop-on-error, and exact return format.
- If the delegated skill requires confirmation, tell Claude Code to stop at the confirmation point and list its questions.
- When Claude Code asks questions, the Decision AI decides whether it can answer from user intent. If not, ask the user.
- Treat Claude Code reports as claims. Verify important outputs locally whenever possible.
- Correct Claude Code when it drifts: missing counts, wrong directories, mojibake, unsafe overwrites, unverified browser claims, or skipped confirmation.

### 5. Permission And Safety Model

Claude Code is usually invoked with:

```text
--allow-dangerously-skip-permissions --permission-mode bypassPermissions
```

This avoids interactive permission stalls. Because `--print` is batch-like, do not expect Claude Code to pause and ask the current assistant for shell permissions. It will usually proceed, fail, or report a blocker.

Therefore the Decision AI must be the permission gate:

- State allowed writes explicitly.
- State forbidden actions explicitly.
- For deletion, require explicit user confirmation for each file before any delete operation.
- For live services, ask before destructive or billing-impacting actions.
- For credentials, never ask Claude Code to print secret values.
- For large file moves, prefer organizing by moving known file types into known folders; do not delete empty directories unless the user confirms.

### 6. Delegation Prompt Template

Use this shape for Claude Code prompts:

```text
@optional-skill-name

Goal:
[one concrete outcome]

Inputs:
- [path/id/url]

Decision AI constraints:
1. Do not delete any files.
2. Only modify these files/directories: [...]
3. Use safe rename if a target exists; do not overwrite unless explicitly allowed.
4. Stop and return the original error if API, auth, permission, or network issues occur.
5. If the skill requires confirmation, stop at that checkpoint and list the questions.
6. Return only: [paths changed], [outputs created], [verification results], [open questions].

Execution details:
[tool/skill-specific instructions]
```

### 7. Verification Protocol

After Claude Code reports completion, verify locally from the Decision AI side.

For files:

- Check paths exist.
- Check modified timestamps and sizes.
- Search for expected markers and absence of placeholders.
- Search for mojibake: `�`, `���`, `锟斤拷`, `Â`, `Ã`, `ä¸`.
- Confirm parent output folders are tidy if the task requires it.

For image/article workflows:

- Confirm Markdown has Cloudinary image links and no stale placeholders.
- Confirm local images landed in the expected `images/` directory.
- Confirm prompt/results JSON landed in the expected `json/` directory.
- Confirm HTML landed in the expected `html/` directory.
- If text artifacts contain wrong mixed-language fragments, ask Claude Code to fix only those text artifacts.

For n8n MCP:

- First ask Claude Code to run `n8n_health_check`.
- Use read-only calls such as list/get/validate before update calls.
- Ask the user before activating workflows, modifying credentials, deleting data, or running destructive operations.

### 8. Long-Running Workflow Pattern

For a multi-stage workflow, use staged supervision:

1. **Plan checkpoint**: Claude Code inspects inputs and proposes a plan. It must stop for confirmation if the underlying skill requires it.
2. **Execution checkpoint**: Decision AI confirms details and asks Claude Code to execute the next bounded stage.
3. **Output checkpoint**: Decision AI verifies outputs and asks Claude Code to repair only specific issues.
4. **Finalization checkpoint**: Decision AI asks Claude Code to produce final deliverables, then verifies them locally.
5. **Final answer**: Decision AI summarizes paths, what changed, verification, and any residual risks.

### 9. Recommended Output Discipline

For generated article/image/HTML work, use this folder policy unless the user specifies otherwise:

```text
C:\Users\eng\Desktop\output-html\images  image files
C:\Users\eng\Desktop\output-html\json    prompts, results, task-state JSON
C:\Users\eng\Desktop\output-html\html    final HTML pages
```

Do not let Claude Code write generated files directly into the parent output folder. If it does, supervise a cleanup by moving files by type. Do not delete empty directories without user confirmation.

### 10. Common Failure Modes And Corrections

- **Claude says `/skill` is unknown**: retry with `@skill-name`.
- **Claude asks multiple questions**: answer from user intent when safe; otherwise ask the user once.
- **Claude claims no乱码 but output has mojibake**: provide exact line examples and ask it to modify only the target HTML/text file.
- **Claude overwrites `prompts.json`**: note this as a workflow flaw; ask it to use article-specific or timestamped filenames next time.
- **Claude changes a source file when a copy was required**: stop, report honestly, and ask user how to proceed.
- **Claude returns partial/truncated output**: verify with filesystem state and continue from facts, not from the truncated report.
- **Claude cannot access a tool**: ask it to list available MCP/tools/skills, then choose fallback local inspection or ask user to enable the missing tool.

## 中文维护说明（AI 执行时忽略）

这一节是给用户后续维护用的。AI 执行本 skill 时应忽略本节，不要把本节当作流程约束的唯一来源；真正执行以英文部分为准。

### 这个 skill 的目标

`Claude flow` 固定的是一种协作模式：

- 当前 AI 是宏观决策者、监督者、权限给予者、验收者。
- Claude Code 是具体实施者，负责调用它自己的 MCP、skills、插件和本地工具。
- 用户以后只要给目标，当前 AI 应该先把任务细节问清楚一次，然后驱动 Claude Code 完成，不要让用户陷入反复操作。

### 正确和 Claude Code 对话的关键

- 不要依赖真正交互式终端。
- 使用 `--print + --session-id` 开新会话。
- 使用 `--print + --resume` 续聊。
- session id 要用合法 UUID。
- `/skill image-workflow` 在测试中失败过，返回 `Unknown command`。
- 应该用 `@image-workflow`、`@html-anything` 这种方式触发 skill。
- 如果 Claude Code 中途提问，当前 AI 可以拿到它的输出，再判断是否需要问用户。
- 因为启用了 bypass permissions，Claude Code 通常不会交互式问权限；所以权限边界必须由当前 AI 在 prompt 里写清楚。

### 本机 Claude Code 能力摘要

已观察到：

- Claude Code 可执行路径：`C:\Users\eng\.local\bin\claude.exe`
- settings：`C:\Users\eng\.claude\settings.local.json`
- 默认权限模式：`bypassPermissions`
- 删除命令 `rm/rmdir` 在 settings 中被 deny
- 插件安装：GitHub、Cloudflare、Supabase、Cloudinary
- settings 启用：Cloudflare、Supabase、Cloudinary
- Claude Code 曾成功调用 n8n MCP：`n8n_health_check`、`n8n_list_workflows`
- Claude Code skills 包括：`image-workflow`、`html-anything`、`n8n-skills`、`playwright-cli`、`obsidian-*` 等

不要把 settings 里的密钥写入 skill 或对话输出。

### 监督重点

- 让 Claude Code 每一步只做一个清晰阶段。
- 关键产物必须由当前 AI 本地复查，不能只信 Claude Code 的总结。
- 对文件生成任务，检查路径、数量、乱码、占位符、输出目录是否符合规则。
- 对 n8n 任务，先 health check/list/get/validate，再考虑 update/activate。
- 删除永远要逐个文件向用户确认。
- 如果 Claude Code 说完成但实际有问题，当前 AI 应该指出具体行号或文件路径，让它只修指定文件。

