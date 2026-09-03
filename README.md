# Agent Circuit Breaker

**GitHub Repository:** [https://github.com/preettrank53/llm-circuit-breaker](https://github.com/preettrank53/llm-circuit-breaker)

A local circuit breaker to stop multi-agent workflows from bankrupting your OpenAI API limits.

<p align="center">
  <img src="assets/demo.gif" alt="Agent Circuit Breaker Demo" width="800"/>
</p>

## Architecture & Data Flow

<p align="center">
  <img src="assets/architecture.png" alt="Architecture Diagram" width="45%"/>
  &nbsp; &nbsp;
  <img src="assets/_-%20visual%20selection.png" alt="Flow Diagram" width="45%"/>
</p>

## Quickstart

1. Create a `.env` file with your upstream API credentials:
   ```env
   UPSTREAM_BASE_URL=https://api.openai.com/v1
   UPSTREAM_API_KEY=your_actual_api_key_here
   ```
2. Start the proxy using Docker Compose:
   ```bash
   docker-compose up -d
   ```

## Usage

Point your AI agent's base URL to the local proxy. It will automatically intercept requests, check your budget, and forward them safely.

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="dummy" # Proxy uses your real key
)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Say hello"}],
    stream=False # Streaming not supported yet
)
print(response.choices[0].message.content)
```

## Management API

Control your budget programmatically:

- **Check Budget:** `GET /v1/budget`
- **Reset Budget:** `POST /v1/budget/reset`
