from __future__ import annotations

import argparse
import glob
import json
import os
import sqlite3
import sys
from dataclasses import dataclass
from json import JSONDecodeError
from pathlib import Path
from typing import Any


MARKERS = {
    "request": "websocket request: ",
    "event": "websocket event: ",
}


@dataclass(frozen=True)
class PayloadMatch:
    kind: str
    payload: Any
    raw_json: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Read Codex SQLite logs and extract websocket JSON payloads."
    )
    parser.add_argument(
        "row_id",
        nargs="?",
        type=int,
        help="Row id in the logs table. Defaults to the latest matching row.",
    )
    parser.add_argument(
        "--db",
        default=None,
        help="Path to the sqlite database. Defaults to the newest ~/.codex/logs_*.sqlite.",
    )
    parser.add_argument(
        "--kind",
        choices=("auto", "request", "event"),
        default="auto",
        help="Payload type to extract.",
    )
    parser.add_argument(
        "--column",
        default=None,
        help="Override the payload column name. Usually not needed.",
    )
    parser.add_argument(
        "--keys",
        action="store_true",
        help="Print top-level keys instead of the full JSON body.",
    )
    parser.add_argument(
        "--raw",
        action="store_true",
        help="Print the raw log line before parsing.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Print compact JSON instead of pretty-printed JSON.",
    )
    parser.add_argument(
        "--meta",
        action="store_true",
        help="Print database path, row id, column, and payload kind to stderr.",
    )
    parser.add_argument(
        "--latest",
        action="store_true",
        help="Use the latest matching row explicitly.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        db_path = resolve_db_path(args.db)
        conn = open_database(db_path)
        column = args.column or detect_payload_column(conn)
        row_id = None if args.latest else args.row_id
        row_id, body = fetch_log_body(conn, column, row_id, args.kind)
        match = extract_payload(body, args.kind)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    finally:
        if "conn" in locals():
            conn.close()

    if args.meta:
        print(
            f"db={db_path} row_id={row_id} column={column} kind={match.kind}",
            file=sys.stderr,
        )

    if args.raw:
        print(body)
        return 0

    if args.keys:
        if not isinstance(match.payload, dict):
            print(
                f"row {row_id} ({match.kind}) payload is {type(match.payload).__name__}, not an object",
                file=sys.stderr,
            )
            return 1
        for key in match.payload.keys():
            print(key)
        return 0

    dump_json(match.payload, compact=args.compact)
    return 0


def resolve_db_path(raw_path: str | None) -> Path:
    if raw_path:
        path = Path(os.path.expanduser(raw_path)).resolve()
        if not path.exists():
            raise FileNotFoundError(f"database not found: {path}")
        return path

    matches = sorted(
        (
            Path(path).resolve()
            for path in glob.glob(os.path.expanduser("~/.codex/logs_*.sqlite"))
        ),
        key=lambda path: (extract_suffix_number(path), path.stat().st_mtime),
        reverse=True,
    )
    if not matches:
        raise FileNotFoundError("no ~/.codex/logs_*.sqlite files found")
    return matches[0]


def extract_suffix_number(path: Path) -> int:
    stem = path.stem
    suffix = stem.rsplit("_", 1)[-1]
    return int(suffix) if suffix.isdigit() else -1


def open_database(path: Path) -> sqlite3.Connection:
    uri = f"file:{path}?mode=ro"
    return sqlite3.connect(uri, uri=True)


def detect_payload_column(conn: sqlite3.Connection) -> str:
    rows = conn.execute("pragma table_info(logs)").fetchall()
    columns = [row[1] for row in rows]
    for candidate in ("message", "feedback_log_body"):
        if candidate in columns:
            return candidate
    raise RuntimeError(
        "could not find a supported payload column in logs; expected message or feedback_log_body"
    )


def fetch_log_body(
    conn: sqlite3.Connection, column: str, row_id: int | None, kind: str
) -> tuple[int, str]:
    if row_id is not None:
        row = conn.execute(f"select id, {column} from logs where id = ?", (row_id,)).fetchone()
        if row is None:
            raise LookupError(f"row id {row_id} not found")
        if row[1] is None:
            raise LookupError(f"row id {row_id} has no {column} value")
        return int(row[0]), str(row[1])

    where_clause, params = build_marker_filter(column, kind)
    row = conn.execute(
        f"select id, {column} from logs where {where_clause} order by id desc limit 1",
        params,
    ).fetchone()
    if row is None:
        raise LookupError("no websocket payload rows found")
    return int(row[0]), str(row[1])


def build_marker_filter(column: str, kind: str) -> tuple[str, tuple[str, ...]]:
    if kind in MARKERS:
        return f"{column} like ?", (f"%{MARKERS[kind]}%",)

    return (
        f"{column} like ? or {column} like ?",
        tuple(f"%{marker}%" for marker in MARKERS.values()),
    )


def extract_payload(body: str, kind: str) -> PayloadMatch:
    kinds = [kind] if kind in MARKERS else list(MARKERS)

    for candidate in kinds:
        marker = MARKERS[candidate]
        index = body.rfind(marker)
        if index == -1:
            continue
        raw_json = body[index + len(marker) :].strip()
        return PayloadMatch(
            kind=candidate,
            payload=decode_json(raw_json),
            raw_json=raw_json,
        )

    json_start = find_json_start(body)
    if json_start is None:
        available = ", ".join(MARKERS.values())
        raise ValueError(f"no websocket marker found; expected one of: {available}")

    raw_json = body[json_start:].strip()
    return PayloadMatch(kind="unknown", payload=decode_json(raw_json), raw_json=raw_json)


def find_json_start(body: str) -> int | None:
    decoder = json.JSONDecoder()
    for index, char in enumerate(body):
        if char not in "[{":
            continue
        try:
            decoder.raw_decode(body[index:])
        except JSONDecodeError:
            continue
        return index
    return None


def decode_json(raw_json: str) -> Any:
    try:
        return json.loads(raw_json)
    except JSONDecodeError as exc:
        raise ValueError(f"failed to parse JSON payload: {exc}") from exc


def dump_json(payload: Any, compact: bool) -> None:
    if compact:
        print(json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
        return
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
