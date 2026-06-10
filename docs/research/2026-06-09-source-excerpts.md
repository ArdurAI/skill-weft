# Source excerpts for SkillHub integration research

Date: 2026-06-09

This file records concise source excerpts collected during the adoption/integration research so the main memo does not need to commit raw HTML captures.

## Model Context Protocol

Source: https://modelcontextprotocol.io/docs/getting-started/intro

Excerpt captured via browser snapshot:

> MCP (Model Context Protocol) is an open-source standard for connecting AI applications to external systems. Using MCP, AI applications like Claude or ChatGPT can connect to data sources, tools, and workflows.

Source: https://modelcontextprotocol.io/specification/2025-06-18/basic/transports

Excerpt captured via browser snapshot:

> The protocol currently defines two standard transport mechanisms for client-server communication: stdio and Streamable HTTP. Clients should support stdio whenever possible.

Source: https://modelcontextprotocol.io/docs/develop/build-with-agent-skills

Excerpt captured from the fetched MCP docs page:

> Agent skills are portable instruction sets that give AI coding assistants domain knowledge for a task.

> Each skill ships a `SKILL.md` file plus a `references/` folder of supporting material ... that the agent reads on demand. The files follow the open format and work with any agent that implements the standard.

## Cursor

Source: https://cursor.com/docs/skills.md

Excerpts:

> Agent Skills is an open standard for extending AI agents with specialized capabilities. Skills package domain-specific knowledge and workflows that agents can use to perform specific tasks.

> A skill is a portable, version-controlled package that teaches agents how to perform domain-specific tasks. Skills can include scripts, templates, and references that agents may act on using their tools.

> Skills load resources on demand, keeping context usage efficient.

> Skills are automatically loaded from `.agents/skills/`, `.cursor/skills/`, `~/.agents/skills/`, and `~/.cursor/skills/`.

> For compatibility, Cursor also loads skills from Claude and Codex directories: `.claude/skills/`, `.codex/skills/`, `~/.claude/skills/`, and `~/.codex/skills/`.

Source: https://cursor.com/docs/rules.md

Excerpts:

> Rules provide system-level instructions to Agent. They bundle prompts, scripts, and more together, making it easy to manage and share workflows across your team.

> Project Rules are stored in `.cursor/rules`, version-controlled and scoped to your codebase.

> Rule contents are included at the start of the model context.

Source: https://cursor.com/docs/mcp.md

Excerpts:

> Model Context Protocol (MCP) enables Cursor to connect to external tools and data sources.

> Write MCP servers in any language that can print to `stdout` or serve an HTTP endpoint - Python, JavaScript, Go, etc.

> Cursor supports three transport methods: `stdio`, `SSE`, and `Streamable HTTP`.

> Browse the Cursor Marketplace for official plugins with one-click install ... Click “Add to Cursor” on a marketplace entry to install it and authenticate with OAuth.

Source: https://cursor.com/docs/cli/headless.md

Excerpts:

> Use Cursor CLI in scripts and automation workflows for code analysis, generation, and refactoring tasks.

> Use print mode (`-p, --print`) for non-interactive scripting and automation.

## Claude Code

Source: local `claude --help`, captured 2026-06-09.

Excerpts:

> Claude Code starts an interactive session by default, use `-p/--print` for non-interactive output.

> `--append-system-prompt` appends a system prompt to the default system prompt.

> In bare mode, explicit context can be provided via `--system-prompt[-file]`, `--append-system-prompt[-file]`, `--add-dir`, `--mcp-config`, `--settings`, `--agents`, and `--plugin-dir`.

> `--mcp-config` loads MCP servers from JSON files or strings.

> `--strict-mcp-config` only uses MCP servers from `--mcp-config`, ignoring all other MCP configurations.

Source: local `claude mcp add --help`, captured 2026-06-09.

Excerpts:

> `claude mcp add [options] <name> <commandOrUrl> [args...]` adds an MCP server to Claude Code.

> Examples include HTTP servers, HTTP servers with headers, stdio servers with environment variables, and stdio servers with subprocess flags.

## Codex

Source: https://raw.githubusercontent.com/openai/codex/main/README.md

Excerpts:

> Codex CLI is a coding agent from OpenAI that runs locally on your computer.

> If you want Codex in your code editor (VS Code, Cursor, Windsurf), install in your IDE. If you want the desktop app experience, run `codex app`.

Source: local `codex --help`, captured 2026-06-09.

Excerpts:

> Codex commands include `exec`, `mcp`, `plugin`, `mcp-server`, `app`, and `remote-control`.

Source: local `codex exec --help`, captured 2026-06-09.

Excerpts:

> `codex exec` runs Codex non-interactively.

> If the prompt is not provided, or if `-` is used, instructions are read from stdin. If stdin is piped and a prompt is also provided, stdin is appended as a `<stdin>` block.

Source: https://developers.openai.com/codex/mcp

Excerpts:

> Codex supports MCP servers in both the CLI and the IDE extension.

> Supported MCP features include STDIO servers and Streamable HTTP servers.

> Codex reads the MCP `instructions` field returned during initialization and uses it as server-wide guidance alongside the server’s tools.

> Codex stores MCP configuration in `config.toml`; by default this is `~/.codex/config.toml`, but project-scoped `.codex/config.toml` is also supported in trusted projects.

> The CLI and IDE extension share this configuration.

## Gemini CLI

Source: local `gemini --help`, captured 2026-06-09.

Excerpts:

> Gemini CLI defaults to interactive mode. Use `-p/--prompt` for non-interactive headless mode.

> Commands include `gemini mcp`, `gemini extensions`, `gemini skills`, and `gemini hooks`.

> `--allowed-mcp-server-names` restricts allowed MCP server names.

Source: local `gemini skills --help`, captured 2026-06-09.

Excerpts:

> `gemini skills` manages agent skills.

> `gemini skills install <source>` installs an agent skill from a git repository URL or local path.

> `gemini skills link <path>` links an agent skill from a local path. Updates to the source are reflected immediately.

Source: local `gemini mcp add --help`, captured 2026-06-09.

Excerpts:

> `gemini mcp add [options] <name> <commandOrUrl> [args...]` adds an MCP server.

> Transport types include `stdio`, `sse`, and `http`.

> Options include `--scope`, `--env`, `--header`, `--timeout`, `--trust`, `--include-tools`, and `--exclude-tools`.

Source: https://raw.githubusercontent.com/google-gemini/gemini-cli/main/docs/tools/mcp-server.md

Excerpts:

> An MCP server exposes tools and resources to Gemini CLI through the Model Context Protocol.

> Gemini CLI integrates with MCP servers through discovery and execution.

> Gemini CLI supports Stdio, SSE, and Streamable HTTP transports.

> Gemini CLI uses the `mcpServers` configuration in `settings.json` to locate and connect to MCP servers.

## Hermes

Source: local `hermes mcp --help`, captured 2026-06-09.

Excerpts:

> Hermes MCP commands include `serve`, `add`, `remove`, `list`, `test`, `configure`, `catalog`, and `install`.

> `hermes mcp serve` runs Hermes as an MCP server.

Source: local `hermes skills --help`, captured 2026-06-09.

Excerpts:

> Hermes skills commands include `browse`, `search`, `install`, `inspect`, `list`, `check`, `update`, `audit`, `uninstall`, `publish`, `tap`, and `config`.

> Hermes manages skills from skills.sh, well-known agent skill endpoints, GitHub, ClawHub, and other registries.
