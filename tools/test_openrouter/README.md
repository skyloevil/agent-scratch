# test_openrouter

一个用于验证 Anthropic 兼容聊天接口是否可访问、鉴权是否生效的最小测试工具。

当前脚本会读取本地 `.env` 中的配置，向 `POST {ANTHROPIC_BASE_URL}/messages` 发起一次请求，请求体固定为一条用户消息 `只回复 pong`，并打印响应状态码、`content-type` 和返回体。

## 环境要求

- Python `3.12+`
- `uv`
- 可用的 Anthropic 兼容接口地址

## 配置

在 `tools/test_openrouter/.env` 中设置以下环境变量：

```env
ANTHROPIC_AUTH_TOKEN=your_token
ANTHROPIC_BASE_URL=https://your-endpoint.example.com/v1
ANTHROPIC_MODEL=your-model-id
```

说明：

- `ANTHROPIC_AUTH_TOKEN`：接口鉴权 token
- `ANTHROPIC_BASE_URL`：接口基础地址，脚本会自动拼接 `/messages`
- `ANTHROPIC_MODEL`：请求使用的模型名

## 安装依赖

```bash
cd tools/test_openrouter
uv sync
```

## 运行

```bash
cd tools/test_openrouter
uv run python main.py
```

## 预期结果

请求成功时，输出会包含：

- `status_code = 200`
- 返回头中的 `content-type`
- JSON 响应体
- `验证结果：接口可访问，鉴权已通过。`

如果配置缺失，脚本会直接退出并提示缺少哪个环境变量。

如果接口返回非 2xx，脚本会打印 HTTP 状态码和响应正文，随后抛出异常，便于排查鉴权、路由或模型配置问题。
