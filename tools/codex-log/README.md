# codex-log

`codex-log` is a small CLI for reading Codex local SQLite logs and extracting websocket request or event payloads as JSON.

It is useful when you want to inspect the exact structured payload sent to or received from Codex without manually searching through raw log rows.

## What It Does

- finds the newest `~/.codex/logs_*.sqlite` database by default
- supports both `message` and `feedback_log_body` log schemas
- extracts websocket request and event payloads from matching rows
- prints either pretty JSON, compact JSON, raw log text, or top-level keys

## Requirements

- Python `3.12+`
- `uv`
- at least one local Codex SQLite log database

## Run

From this directory:

```bash
uv run codex-log 64045
uv run codex-log --latest
uv run codex-log --latest --kind event --keys
uv run codex-log --db ~/.codex/logs_123.sqlite --meta
```

## Common Options

- `row_id`: read a specific row from the `logs` table
- `--latest`: explicitly use the newest matching row
- `--kind {auto,request,event}`: choose which payload type to extract
- `--keys`: print only top-level JSON keys
- `--raw`: print the raw matching log body instead of parsed JSON
- `--compact`: print compact JSON without indentation
- `--meta`: print database path, row id, column, and detected payload kind to stderr
- `--column`: manually override the payload column if needed

## Tests

```bash
uv run python -m unittest discover -s tests -v
```

## Notes

- If no row id is provided, the CLI searches for the newest row containing a websocket payload marker.
- If no known marker is found, it falls back to the first decodable JSON object or array in the log body.
- Errors are reported to stderr and return a non-zero exit status.
