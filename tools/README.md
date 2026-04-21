# tools

This directory contains internal tools, scripts, and diagnostics used to support development work in the repository.

## Current Tools

- `codex-log/`: inspect Codex SQLite logs and extract websocket request or event payload JSON
- `test_openrouter/`: verify an Anthropic-compatible endpoint with a minimal authenticated request

## Conventions

Tools in this directory should prefer:

- a focused scope
- a clear command-line entry point
- a local `README.md` with setup and usage instructions
- explicit environment variable documentation when secrets or external endpoints are required
