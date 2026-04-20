import unittest

from codex_log.cli import PayloadMatch, extract_payload, find_json_start


class CliParsingTests(unittest.TestCase):
    def test_extract_request_payload(self) -> None:
        body = 'prefix websocket request: {"type":"response.create","model":"gpt-5.4"}'
        match = extract_payload(body, "auto")
        self.assertEqual(
            match,
            PayloadMatch(
                kind="request",
                payload={"type": "response.create", "model": "gpt-5.4"},
                raw_json='{"type":"response.create","model":"gpt-5.4"}',
            ),
        )

    def test_extract_event_payload(self) -> None:
        body = 'prefix websocket event: {"type":"response.output_text.delta","delta":"hi"}'
        match = extract_payload(body, "event")
        self.assertEqual(match.kind, "event")
        self.assertEqual(match.payload["delta"], "hi")

    def test_fallback_to_first_json_object(self) -> None:
        body = 'prefix no marker here {"type":"response.create","input":[]}'
        match = extract_payload(body, "auto")
        self.assertEqual(match.kind, "unknown")
        self.assertEqual(match.payload, {"type": "response.create", "input": []})

    def test_find_json_start_returns_none_without_json(self) -> None:
        self.assertIsNone(find_json_start("plain text only"))

    def test_invalid_json_raises_helpful_error(self) -> None:
        body = 'prefix websocket request: {"type":'
        with self.assertRaisesRegex(ValueError, "failed to parse JSON payload"):
            extract_payload(body, "request")


if __name__ == "__main__":
    unittest.main()
