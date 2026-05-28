# Claude Code Environment Snapshot

This reference records observed local Claude Code capabilities. Treat it as a snapshot, not a guarantee. Re-check with Claude Code at the start of tasks that depend on a specific tool.

## Entrypoint

- Executable: `C:\Users\eng\.local\bin\claude.exe`
- Settings: `C:\Users\eng\.claude\settings.local.json`
- Recommended mode: `--print --output-format text --allow-dangerously-skip-permissions --permission-mode bypassPermissions`

## Permission Model

- Default mode: `bypassPermissions`
- Allowed categories include common shell, node/npm/python, read/write/edit, git, docker, curl.
- Denied categories include `rm`, `rmdir`, and `rm -*`.
- Do not expect interactive permission prompts in `--print` mode.

## Plugins

Installed plugin cache includes:

- `github@claude-plugins-official`
- `cloudflare@claude-plugins-official`
- `supabase@claude-plugins-official`
- `cloudinary@claude-plugins-official`

Enabled in local settings:

- Cloudflare
- Supabase
- Cloudinary

## Skills

Observed user skills under `C:\Users\eng\.claude\skills` include:

- `brand-guidelines`
- `frontend-design`
- `html-anything`
- `humanizer`
- `image-workflow`
- `mcp-builder`
- `n8n-skills`
- `notebooklm`
- `obsidian-bases`
- `obsidian-cli`
- `obsidian-markdown`
- `playwright-cli`
- `prompt-guard`
- `skill-creator`
- `web-video-presentation`

## MCP Notes

Claude Code has previously reported successful access to n8n MCP:

- `n8n_health_check`
- `n8n_list_workflows`
- `n8n_get_workflow`
- `n8n_create_workflow`
- `n8n_update_full_workflow`
- `n8n_validate_workflow`
- `n8n_executions`
- `search_nodes`
- `search_templates`

Always verify with a fresh `n8n_health_check` or read-only list call before depending on these tools.

## Security Note

Do not copy or reveal credential values from Claude settings, `.env` files, or plugin config. It is enough to say that credentials are configured or missing.
