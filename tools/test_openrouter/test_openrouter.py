from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any

import httpx
from dotenv import load_dotenv

ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MAX_TOKENS = 64
DEFAULT_PROMPT = "只回复 pong"


@dataclass(frozen=True)
class AnthropicConfig:
    token: str
    base_url: str
    model: str

    @property
    def messages_url(self) -> str:
        return f"{self.base_url}/messages"


def load_config() -> AnthropicConfig:
    load_dotenv()

    token = os.getenv("ANTHROPIC_AUTH_TOKEN")
    base_url = os.getenv("ANTHROPIC_BASE_URL", "").rstrip("/")
    model = os.getenv("ANTHROPIC_MODEL")

    if not token:
        raise SystemExit("缺少 ANTHROPIC_AUTH_TOKEN")
    if not base_url:
        raise SystemExit("缺少 ANTHROPIC_BASE_URL")
    if not model:
        raise SystemExit("缺少 ANTHROPIC_MODEL")

    return AnthropicConfig(token=token, base_url=base_url, model=model)


def build_headers(config: AnthropicConfig) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {config.token}",
        "Content-Type": "application/json",
        "anthropic-version": ANTHROPIC_VERSION,
    }


def build_payload(config: AnthropicConfig) -> dict[str, Any]:
    return {
        "model": config.model,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "messages": [{"role": "user", "content": DEFAULT_PROMPT}],
    }


def send_probe_request(config: AnthropicConfig) -> httpx.Response:
    with httpx.Client(timeout=60.0) as client:
        return client.post(
            config.messages_url,
            headers=build_headers(config),
            json=build_payload(config),
        )


def print_response(response: httpx.Response) -> None:
    print("status_code =", response.status_code)
    print("headers content-type =", response.headers.get("content-type"))
    try:
        data = response.json()
        print(json.dumps(data, ensure_ascii=False, indent=2))
    except ValueError:
        print(response.text)


def main() -> None:
    config = load_config()

    try:
        response = send_probe_request(config)
        print_response(response)
        response.raise_for_status()
        print("\n验证结果：接口可访问，鉴权已通过。")
    except httpx.HTTPStatusError as exc:
        print("\nHTTP错误：")
        print("status =", exc.response.status_code)
        print(exc.response.text)
        raise
    except Exception as exc:
        print("\n请求失败：", repr(exc))
        raise


if __name__ == "__main__":
    main()
