# test_openrouter

`test_openrouter` is a minimal probe tool for verifying that an Anthropic-compatible chat endpoint is reachable and that authentication succeeds.

The script loads configuration from a local `.env` file, sends a single `POST {ANTHROPIC_BASE_URL}/messages` request, and prints the response status code, response content type, and response body.

## Requirements

- Python `3.12+`
- `uv`
- an accessible Anthropic-compatible endpoint

## Configuration

Create `tools/test_openrouter/.env` with the following variables:

```env
ANTHROPIC_AUTH_TOKEN=your_token
ANTHROPIC_BASE_URL=https://your-endpoint.example.com/v1
ANTHROPIC_MODEL=your-model-id
```

Variable meanings:

- `ANTHROPIC_AUTH_TOKEN`: bearer token used for authentication
- `ANTHROPIC_BASE_URL`: base API URL; the script automatically appends `/messages`
- `ANTHROPIC_MODEL`: model identifier sent in the request payload

## Install Dependencies

```bash
cd tools/test_openrouter
uv sync
```

## Run

```bash
cd tools/test_openrouter
uv run python main.py
```

## Request Behavior

The probe sends a single user message with the fixed content `只回复 pong` and uses a small `max_tokens` value so the response stays lightweight.

## Expected Output

On success, the output includes:

- `status_code = 200`
- the response `content-type`
- the parsed JSON body, when available
- `验证结果：接口可访问，鉴权已通过。`

If configuration is missing, the script exits immediately and reports which environment variable is absent.

If the endpoint returns a non-2xx response, the script prints the HTTP status code and response body before re-raising the error for debugging.
