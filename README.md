# ToolGuard

> AI application security layer — scan LLM inputs, outputs, and MCP tool calls before they reach your system. Built by **hiveden**.

---

## Architecture

```
 ┌──────────────────────────────────────────────────────────┐
 │                      Client / Agent                      │
 └───────────────────────────┬──────────────────────────────┘
                             │  HTTP
 ┌───────────────────────────▼──────────────────────────────┐
 │                    ToolGuard  :8400                       │
 │                                                           │
 │  POST /scan/input   ──►  PromptInjectionScanner           │
 │  POST /scan/output  ──►  OutputValidationScanner          │
 │  POST /scan/tool-call ► MCPParamCheckScanner              │
 │                                                           │
 │  Scanner Pipeline Engine                                  │
 │  ┌──────────────────────────────────────────────────┐    │
 │  │  scanner[0] → scanner[1] → … → aggregate result  │    │
 │  │  short-circuit on first BLOCK                     │    │
 │  └──────────────────────────────────────────────────┘    │
 └──────────────────────────────────────────────────────────┘
```

---

## Quick Start

```bash
# Using Docker Compose (recommended)
docker compose up -d

# Or install locally
pip install -e .
toolguard
```

The service starts on **port 8400**. Open `http://localhost:8400/docs` for the interactive API docs.

---

## API Reference

### POST `/scan/input`

Scan LLM input messages for prompt injection and other threats.

**Request**
```json
{
  "messages": [{"role": "user", "content": "Hello, world!"}],
  "metadata": {"source": "chat-ui", "session_id": "abc123"}
}
```

**Response**
```json
{
  "decision": "pass",
  "results": [
    {
      "decision": "pass",
      "scanner_name": "prompt_injection",
      "reason": "No prompt injection keywords detected",
      "score": 0.1,
      "metadata": null
    }
  ]
}
```

---

### POST `/scan/output`

Scan LLM output text for safety and policy compliance.

**Request**
```json
{"output": "The answer is 42.", "metadata": {}}
```

**Response**
```json
{"decision": "pass", "results": [...]}
```

---

### POST `/scan/tool-call`

Validate an MCP tool-call invocation before forwarding to the tool.

**Request**
```json
{
  "tool_name": "read_file",
  "arguments": {"path": "/tmp/data.txt"},
  "caller": {"agent_id": "agent-1", "session_id": "sess-xyz"}
}
```

**Response**
```json
{"decision": "pass", "results": [...]}
```

---

### GET `/health`

```json
{
  "status": "healthy",
  "scanners": {
    "input": ["prompt_injection"],
    "output": ["output_validation"],
    "tool_call": ["mcp_param_check"]
  }
}
```

---

## Configuration

Edit `config/toolguard.yaml`:

```yaml
server:
  host: "0.0.0.0"
  port: 8400
  log_level: "info"

scanners:
  input:
    - prompt_injection
  output:
    - output_validation
  tool_call:
    - mcp_param_check

scanner_configs:
  output_validation:
    enabled: true
    config:
      max_output_length: 50000

  mcp_param_check:
    enabled: true
    config:
      max_payload_bytes: 102400
```

Override the config path with the `TOOLGUARD_CONFIG_PATH` environment variable.

---

## Scanner Plugin Interface

Add a new scanner in three steps:

### 1. Create the scanner class

```python
# src/toolguard/scanners/my_scanner.py
from toolguard.scanners.base import BaseScanner, ScanDecision, ScanResult

class MyScanner(BaseScanner):
    @property
    def name(self) -> str:
        return "my_scanner"

    async def scan(self, input_data: dict) -> ScanResult:
        # Implement your logic here.
        return ScanResult(
            decision=ScanDecision.PASS,
            scanner_name=self.name,
            reason="All good",
        )

    def configure(self, config: dict) -> None:
        # Optional: read config keys.
        pass
```

### 2. Register in `toolguard.yaml`

```yaml
scanners:
  input:
    - prompt_injection
    - my_scanner          # <-- add here
```

### 3. Wire into the pipeline factory

In `src/toolguard/api/scan.py`, add your scanner to the appropriate `_build_*_pipeline()` factory function.

---

## Roadmap

| Phase | Milestone | Status |
|-------|-----------|--------|
| **MVP** | FastAPI skeleton, mock scanners, Docker | ✅ Done |
| **V1** | LlamaFirewall prompt injection, Guardrails output validation, OpenTelemetry tracing | 🔜 Next |
| **V2** | Multi-tenant config, rate limiting, async LLM-based scanners, Prometheus metrics | 📋 Planned |

---

## License

MIT © 2026 [hiveden](https://hiveden.ai)
