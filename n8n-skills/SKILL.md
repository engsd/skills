---
name: n8n-skills
description: Aggregated n8n workflow-building expertise for Codex. Use when working with n8n workflows, n8n MCP tools, node configuration, expression syntax, JavaScript or Python Code nodes, validation, debugging, APIMart/OpenRouter HTTP workflows, or reusable n8n automation patterns.
---

# n8n Skills

Use this skill as the single entry point for n8n work. Load only the reference needed for the current task.

## Reference Map

- For JavaScript Code nodes, read `references/n8n-code-javascript/SKILL.md`.
- For Python Code nodes, read `references/n8n-code-python/SKILL.md`.
- For n8n expression syntax, data access, and expression debugging, read `references/n8n-expression-syntax/SKILL.md`.
- For MCP workflow creation, validation, and update tooling, read `references/n8n-mcp-tools-expert/SKILL.md`.
- For exact node configuration and parameter patterns, read `references/n8n-node-configuration/SKILL.md`.
- For workflow validation, test data, error diagnosis, and correction loops, read `references/n8n-validation-expert/SKILL.md`.
- For workflow design patterns, triggers, branching, waits, polling, and HTTP API orchestration, read `references/n8n-workflow-patterns/SKILL.md`.

## Workflow

1. Identify the n8n task type: build, debug, validate, configure a node, write Code node logic, or fix expressions.
2. Read the smallest relevant reference from the map.
3. Prefer exact n8n node schemas and MCP validation over guessed parameter names.
4. Validate workflow code before creating or updating a workflow.
5. When modifying an existing workflow, keep edits scoped to the failing node or requested path unless the user asks for a broader refactor.
6. Never hardcode API keys or bearer tokens in workflow nodes. Use n8n credentials.

## Common Pairings

- HTTP API workflow: read node configuration, expression syntax, and workflow patterns.
- Image generation workflow: read workflow patterns, node configuration, and validation expert.
- Code node error: read the relevant JavaScript or Python Code node reference.
- JSON Body or expression error: read expression syntax and validation expert.
