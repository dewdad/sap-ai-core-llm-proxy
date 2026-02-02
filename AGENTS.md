# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask-based proxy server that transforms SAP AI Core LLM APIs into OpenAI-compatible APIs. It enables any application supporting OpenAI or Anthropic APIs (Cursor IDE, Cline, Cherry Studio, Claude Code, etc.) to work with SAP AI Core services, supporting models like GPT-5, Claude Sonnet 4.5, and Google Gemini 2.5 Pro.

## Environment Setup

**IMPORTANT**: This project should be installed with `uv` in `.venv`:

```bash
uv venv
uv pip install -r requirements.txt
```

## Key Commands

### Running the Proxy Server
```bash
# Standard mode
python proxy_server.py --config config.json

# Debug mode (verbose logging)
python proxy_server.py --config config.json --debug

# Using convenience scripts
./start.sh           # Unix/Linux
./run-proxy.ps1      # Windows PowerShell
```

### Testing
```bash
# Test specific models
python test_gpt.py
python test_sonnet.py
python test_opus.py

# Test deployments
python test_deployment.py

# Demo request
python proxy_server_demo_request.py

# Load testing
python load_testing.py
```

### SAP AI Core Management
```bash
# List available deployments
python list_deployments.py

# List configurations
python list_configurations.py

# Find specific deployment (e.g., Opus)
python find_opus_deployment.py
```

### Interactive Chat
```bash
# Default model
python chat.py

# Specific model
python chat.py --model gpt-4o
```

## Architecture Overview

### Core Components

1. **[proxy_server.py](proxy_server.py)** - Main Flask application (~2000+ lines)
   - Flask server with multiple API endpoints
   - Multi-subAccount configuration with load balancing
   - Token management and caching
   - API format conversion (OpenAI ↔ Claude ↔ Gemini)
   - Connection pool management with HTTP session reuse
   - SAP AI SDK integration with client caching

2. **Configuration System**
   - `config.json` - Main proxy configuration (subAccounts, models, tokens)
   - `~/.aicore/config.json` - SAP AI Core SDK credentials for Anthropic Claude
   - Service key JSON files referenced in config.json

### API Endpoints

The proxy exposes these main endpoints:

- **POST /v1/chat/completions** - OpenAI-compatible chat API (supports all models)
- **POST /v1/messages** - Anthropic Claude Messages API (uses SAP AI SDK)
- **POST /v1/embeddings** - OpenAI-compatible embeddings API
- **GET /v1/models** - List available models
- **GET /health** - Health check endpoint

### Load Balancing Architecture

The proxy implements sophisticated multi-level load balancing:

1. **Cross-subAccount**: Requests for a model are distributed across all subAccounts that have it
2. **Within-subAccount**: Multiple deployment URLs per model are load-balanced
3. **Automatic Failover**: Failed requests automatically retry with different subAccount/deployment
4. **Token Management**: Independent token lifecycle per subAccount

Key classes:
- `ProxyConfig` - Global configuration manager
- `SubAccountConfig` - Individual subAccount configuration
- `TokenInfo` - Thread-safe token caching per subAccount

### API Format Conversion

The proxy converts between multiple API formats:

- **convert_openai_to_claude()** - OpenAI → Claude (for Claude 3.5)
- **convert_openai_to_claude37()** - OpenAI → Claude (for Claude 3.7/4.x)
- **convert_openai_to_gemini()** - OpenAI → Gemini
- **convert_claude_request_to_openai()** - Claude → OpenAI
- **convert_claude_request_to_gemini()** - Claude → Gemini
- **convert_claude_request_for_bedrock()** - Claude → Bedrock format

Both streaming and non-streaming responses are supported with proper SSE formatting.

### Performance Optimizations

1. **HTTP Session Reuse**: Global `_http_session` with connection pooling (50 pools, 100 max connections)
2. **SDK Client Caching**: Reuses SAP AI SDK Session and clients per model to avoid expensive initialization
3. **Token Caching**: Tokens cached per subAccount with automatic refresh (4-hour lifetime, 5-min buffer)
4. **Connection Pool Management**: Proper cleanup with `after_request_cleanup()` hook

### Compatibility Patches

**IMPORTANT**: The codebase includes a monkey patch at [proxy_server.py:31-38](proxy_server.py#L31-L38) that fixes compatibility between `sap-ai-sdk-gen` (gen_ai_hub) and `ai_core_sdk` 2.6.2. The patch filters out the unsupported `client_type` parameter. Do not remove this patch.

## Configuration

### Main Proxy Configuration (config.json)

Structure:
```json
{
  "subAccounts": {
    "subAccount1": {
      "resource_group": "default",
      "service_key_json": "path/to/service_key.json",
      "deployment_models": {
        "model-name": ["deployment-url-1", "deployment-url-2"]
      }
    }
  },
  "secret_authentication_tokens": ["token1", "token2"],
  "port": 3001,
  "host": "127.0.0.1"
}
```

Model names are kept as-is (no prefix normalization). Common model names:
- Claude: `3.5-sonnet`, `3.7-sonnet`, `4-sonnet`, `4.5-sonnet`, `anthropic--claude-4-sonnet`
- OpenAI: `gpt-4o`, `gpt-4.1`, `gpt-5`, `gpt-o3-mini`
- Gemini: `gemini-2.5-pro`

### SAP AI Core SDK Configuration (~/.aicore/config.json)

Required for `/v1/messages` endpoint (Anthropic Claude Messages API):
```json
{
  "AICORE_AUTH_URL": "https://xxx.authentication.sap.hana.ondemand.com",
  "AICORE_CLIENT_ID": "xxx",
  "AICORE_CLIENT_SECRET": "xxx",
  "AICORE_RESOURCE_GROUP": "default",
  "AICORE_BASE_URL": "https://api.ai.xxx.cfapps.sap.hana.ondemand.com/v2"
}
```

## Token Usage Logging

The proxy logs token usage to `logs/token_usage.jsonl` for each request. Format:
```json
{
  "timestamp": "2024-01-13T10:30:00",
  "model": "gpt-4o",
  "subaccount_name": "subAccount1",
  "prompt_tokens": 100,
  "completion_tokens": 50,
  "total_tokens": 150,
  "cost": 0.0025
}
```

Location: `log_token_usage()` function at [proxy_server.py:292](proxy_server.py#L292)

## Docker Support

The project includes a [Dockerfile](Dockerfile) for containerized deployment:

```bash
# Build
docker build -t sap-ai-core-llm-proxy:latest .

# Run
docker run --rm \
  -p 3001:3001 \
  -e PORT=3001 \
  -e HOST=0.0.0.0 \
  -e CONFIG_PATH=/app/config.json \
  -v $(pwd)/config.json:/app/config.json:ro \
  -v $HOME/.aicore:/root/.aicore:ro \
  sap-ai-core-llm-proxy:latest

# Debug mode
docker run --rm -p 3001:3001 -e DEBUG=1 ...
```

## Java Client

A Java client exists in [SAPAICoreJavaClient/](SAPAICoreJavaClient/) using Gradle:

```bash
cd SAPAICoreJavaClient
./gradlew build
```

## Integration Examples

### Claude Code
```bash
export ANTHROPIC_AUTH_TOKEN=your_secret_key
export ANTHROPIC_BASE_URL=http://127.0.0.1:3001
export ANTHROPIC_MODEL=anthropic--claude-4-sonnet
claude
```

### Cursor IDE
Configure in settings with:
- Base URL: http://127.0.0.1:3001/v1
- API Key: one of `secret_authentication_tokens`
- Model: e.g., `gpt-4o` (Cursor blocks model names containing "claude")

### Cline
Choose "OpenAI API Compatible":
- Base URL: http://127.0.0.1:3001/v1
- API key: one of `secret_authentication_tokens`
- Model ID: e.g., `4-sonnet`

## Debugging Sessions Repository

**IMPORTANT**: Before debugging any issue, check the `debugging/` folder for documented past sessions.

### Location: `debugging/`

This folder contains structured documentation of past debugging and repair sessions. Each session captures:
- Problem description and error signatures
- Root cause analysis with investigation steps
- Solution applied with code changes
- Prevention recommendations

### How to Use When Debugging

1. **Search first**: Check `debugging/README.md` for the session index and search existing sessions by error patterns
2. **Reference solutions**: Past sessions may contain directly applicable fixes
3. **Document new issues**: When resolving new issues, create a session file using `debugging/TEMPLATE.md`

### Session File Structure
```
debugging/
├── README.md                              # Index and search instructions
├── TEMPLATE.md                            # Template for new sessions
├── VERIFICATION_CHECKLIST.md              # MANDATORY checklist before marking RESOLVED
└── YYYY-MM-DD_category-description.md     # Individual session files
```

### Quick Search Commands
```powershell
# Search for error patterns in debugging sessions
Get-ChildItem -Path debugging -Filter "*.md" | Select-String "error text"

# List all resolved sessions
Get-ChildItem -Path debugging -Filter "*.md" | Select-String "RESOLVED"
```

### ⚠️ MANDATORY: Verification Before Resolution

**DO NOT claim any proxy issue is RESOLVED until the following tests pass:**

1. **Run the Claude Code Integration Test:**
   ```bash
   python test_claude_code_integration.py --http-only --save-output
   ```

2. **Complete the Verification Checklist:**
   - Review `debugging/VERIFICATION_CHECKLIST.md`
   - Check all applicable items
   - Include test output in the debugging session file

3. **For Full Verification (optional but recommended):**
   ```bash
   python test_claude_code_integration.py --save-output
   ```

The Claude Code integration test validates:
- Proxy can handle real Claude Code workloads
- API format conversion works correctly
- Token authentication works
- Response handling is correct

**If the test fails, the issue is NOT resolved. Continue debugging.**

## Important Debugging Notes

1. **Connection Pool Exhaustion**: Fixed in recent commits by increasing pool size and implementing proper cleanup
2. **Token Issues**: Check token expiry and refresh logic in `fetch_token()`
3. **Model Detection**: Model type detection uses prefixes - see `is_claude_model()`, `is_claude_37_or_4()`, `is_gemini_model()`
4. **Streaming Issues**: Both OpenAI and Claude formats supported; check chunk conversion functions
5. **SDK Compatibility**: The monkey patch for `client_type` AND authentication credential injection is critical for SAP AI SDK integration
6. **SDK Authentication**: The monkey patch at `_patched_from_env()` injects `auth_url`, `client_id`, `client_secret` from proxy config service keys (see [SDK-AUTH-001](debugging/2026-02-02_sdk-authentication-fix.md))

## Code Style Notes

- Extensive logging at INFO/DEBUG levels
- Thread-safe operations using locks for token management
- Dataclasses used for configuration objects
- Flask `stream_with_context()` for proper streaming responses
- Explicit response cleanup with `response.close()` to prevent connection leaks

## Additional Resources

- [README.md](README.md) - Comprehensive setup and usage guide
- [docs/ClaudeCodeGuideline.md](docs/ClaudeCodeGuideline.md) - Detailed Claude Code integration guide
- SAP AI Core documentation: https://developers.sap.com/tutorials/ai-core-generative-ai.html
- SAP AI SDK docs: https://help.sap.com/doc/generative-ai-hub-sdk/CLOUD/en-US/_reference/README_sphynx.html
