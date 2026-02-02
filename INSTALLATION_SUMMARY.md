# SAP AI Core LLM Proxy - Installation Summary

## Installation Completed Successfully ✅

**Date:** January 13, 2026  
**Location:** `/Users/i071496/Tools/sap-ai-core-llm-proxy`

## What Was Done

1. ✅ Created the Tools directory at `/Users/i071496/Tools`
2. ✅ Cloned the repository from https://github.com/pjq/sap-ai-core-llm-proxy
3. ✅ Copied configuration files from OneDrive:
   - `config.json` (909 bytes)
   - `key.json` (686 bytes)
4. ✅ Created Python virtual environment in `venv/`
5. ✅ Installed all dependencies from `requirements.txt`
6. ✅ Created `start.sh` startup script

## Configuration Overview

Your proxy is configured with:
- **Host:** 127.0.0.1
- **Port:** 4337
- **Models:**
  - gpt-5
  - claude-sonnet-4.5
  - claude-opus-4.5
- **Authentication:** Using service key from `key.json`

## How to Use

### Start the Proxy Server

```bash
cd /Users/i071496/Tools/sap-ai-core-llm-proxy
./start.sh
```

Or manually:
```bash
cd /Users/i071496/Tools/sap-ai-core-llm-proxy
source venv/bin/activate
python proxy_server.py --config config.json
```

### With Debug Mode

```bash
source venv/bin/activate
python proxy_server.py --config config.json --debug
```

### Stop the Server

Press `Ctrl+C` in the terminal where the server is running.

## Endpoints

Once running, the proxy will be available at:
- **Base URL:** http://127.0.0.1:4337
- **OpenAI-compatible endpoint:** http://127.0.0.1:4337/v1/chat/completions

## Authentication

Use one of the tokens from your `config.json`:
- `sk-my-secret-key-123`
- `sk-another-key-456`

Example curl command:
```bash
curl http://127.0.0.1:4337/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-my-secret-key-123" \
  -d '{
    "model": "claude-sonnet-4.5",
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## Directory Structure

```
/Users/i071496/Tools/sap-ai-core-llm-proxy/
├── venv/                    # Python virtual environment
├── config.json              # Configuration file (copied from OneDrive)
├── key.json                 # Service key (copied from OneDrive)
├── start.sh                 # Convenience startup script
├── proxy_server.py          # Main proxy server
├── requirements.txt         # Python dependencies
└── README.md               # Original documentation
```

## Notes

- The virtual environment is automatically activated when using `start.sh`
- Configuration files were copied from your OneDrive repository
- All dependencies have been installed successfully
- The proxy acts as an OpenAI-compatible endpoint for SAP AI Core models

## Troubleshooting

If you encounter any issues:

1. Check that the virtual environment is activated:
   ```bash
   which python  # Should show: .../venv/bin/python
   ```

2. Verify config files are present:
   ```bash
   ls -la config.json key.json
   ```

3. Check the proxy server help:
   ```bash
   source venv/bin/activate
   python proxy_server.py --help
   ```

4. Run with debug mode for more information:
   ```bash
   python proxy_server.py --config config.json --debug
   ```
