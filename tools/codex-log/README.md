# codex-log

Inspect Codex local SQLite logs and pretty-print websocket request or event JSON.

## Run

```bash
uv run codex-log 64045
uv run codex-log --latest
uv run codex-log --latest --kind event --keys
uv run python -m unittest discover -s tests -v
```

## Notes

- Defaults to the newest `~/.codex/logs_*.sqlite`.
- Handles both old `message` schemas and newer `feedback_log_body` schemas.
- When no row id is given, it selects the newest row containing a websocket payload.
