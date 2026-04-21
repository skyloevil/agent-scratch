# agent-scratch

`agent-scratch` is a small monorepo for experimenting with application code, backend services, shared libraries, and internal developer tools in one place.

## Repository Layout

- `apps/`: user-facing applications such as web apps, CLIs, or desktop clients
- `services/`: backend APIs, workers, scheduled jobs, and service processes
- `libs/`: shared packages, reusable helpers, and cross-project modules
- `tools/`: operational scripts and internal utilities used during development

## Current Contents

The repository is intentionally minimal at the moment.

- `tools/codex-log/`: inspect Codex local SQLite log rows and extract websocket request or event payloads
- `tools/test_openrouter/`: send a small Anthropic-compatible probe request to verify endpoint reachability and authentication

The `apps/`, `services/`, and `libs/` layers are currently placeholders and are ready for future projects.

## Working Style

Each top-level layer should keep its own `README.md` up to date so the purpose, ownership, and entry points of that directory remain obvious.

When a new project is added, prefer documenting:

- what the project does
- how to run or test it
- required environment variables or external dependencies
- where its public entry points live
