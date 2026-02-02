# Debugging Session: Cache Control in Tools Causes Bedrock Validation Error

**Date**: 2026-02-02
**Status**: ✅ RESOLVED (verified working)
**Category**: API Format Conversion / Bedrock Compatibility
**Related Files**: `proxy_server.py`

## Problem Description

Claude Code integration fails with Bedrock API validation error when using tools.

### Error Message
```
An error occurred (ValidationException) when calling the InvokeModel operation: tools.19.custom.cache_control.ephemeral.scope: Extra inputs are not permitted
```

### Error Location
```python
File "proxy_server.py", line 2525, in proxy_claude_request
    response = bedrock.invoke_model(body=body_json)
```

## Root Cause Analysis

### Investigation Steps

1. Analyzed the error message - it indicates that `tools[19].custom.cache_control.ephemeral.scope` contains extra fields not permitted by Bedrock
2. Reviewed the `proxy_claude_request` function in `proxy_server.py`
3. Found existing `strip_cache_control` function that recursively removes `cache_control` fields
4. Discovered the function was only being applied to `system` and `messages` fields, but NOT to `tools`

### Root Cause

Claude Code sends `cache_control` fields inside the `tools` array for caching purposes. The Bedrock API doesn't support these extended cache control parameters. The existing code was stripping `cache_control` from `system` and `messages`, but the same sanitization was not applied to `tools`.

## Solution Applied

Two fixes were needed:
1. Strip `cache_control` fields from the `tools` array
2. Remove the `custom` field entirely from tools (Bedrock doesn't support custom fields)

### Code Changes

Location: `proxy_server.py`, in the `proxy_claude_request()` function

**Fix 1: Strip cache_control from tools**
```python
# Strip cache_control from tools (Claude Code sends cache_control in tools that Bedrock doesn't support)
if "tools" in body:
    original_tools = json.dumps(body["tools"])
    body["tools"] = strip_cache_control(body["tools"])
    if original_tools != json.dumps(body["tools"]):
        logging.info(f"[{request_id}] Stripped cache_control from tools")
```

**Fix 2: Remove 'custom' field from tools**
```python
# Remove 'custom' field from tools (Bedrock doesn't support custom fields in tools)
if "tools" in body and isinstance(body["tools"], list):
    for tool in body["tools"]:
        if isinstance(tool, dict) and "custom" in tool:
            tool.pop("custom", None)
            logging.info(f"[{request_id}] Removed 'custom' field from tool: {tool.get('name', 'unknown')}")
```

## The `strip_cache_control` Function

The existing helper function recursively strips `cache_control` from all nested dictionaries and lists:

```python
def strip_cache_control(obj):
    """Recursively strip cache_control fields from dicts and lists."""
    if isinstance(obj, dict):
        # Remove cache_control key if present
        obj.pop("cache_control", None)
        # Recursively process all values
        for key, value in list(obj.items()):
            obj[key] = strip_cache_control(value)
        return obj
    elif isinstance(obj, list):
        return [strip_cache_control(item) for item in obj]
    else:
        return obj
```

## Verification Steps

1. Restart the proxy server:
   ```bash
   python proxy_server.py --config config.json
   ```

2. Run the Claude Code integration test:
   ```bash
   python test_claude_code_integration.py --http-only --save-output
   ```

3. Test with actual Claude Code by making requests that include tools

## Prevention Recommendations

1. When adding support for new Claude API fields, always check if Bedrock supports them
2. The `strip_cache_control` function should be applied to ALL request body fields that may contain nested cache_control, not just specific ones
3. Consider implementing a more comprehensive field sanitization that applies to the entire request body

## Related Issues

- Previous fix for `system.cache_control`: Same pattern, different field location
- Similar to SDK authentication fix documented in `2026-02-02_sdk-authentication-fix.md`

## Verification Results

Test with tools containing `cache_control` and `custom` fields:
```
Status: 200
Response: {"content":[{"id":"toolu_bdrk_01VQX9dcLa2iwFNKNRRwr6qB","input":{"expression":"2+2"},"name":"calculator","type":"tool_use"}],...}
```

Logs showing successful sanitization:
```
[1770024559677-9942] Stripped cache_control from tools
[1770024559677-9942] Removed 'custom' field from tool: calculator
```

Cleaned request body sent to Bedrock:
```json
{
  "tools": [
    {
      "name": "calculator",
      "description": "A simple calculator",
      "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}}
    }
  ]
}
```

## Logs to Monitor

After applying the fix, look for these log messages:
```
[request_id] Stripped cache_control from tools
[request_id] Removed 'custom' field from tool: <tool_name>
