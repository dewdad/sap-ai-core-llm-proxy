# Debugging Verification Checklist

**MANDATORY**: This checklist must be completed before marking ANY debugging session as ✅ RESOLVED.

## Purpose

Ensures that proxy repairs are properly tested and validated before claiming resolution. The Claude Code integration test is particularly important because it tests the proxy end-to-end with a real AI assistant workload.

---

## Pre-Resolution Checklist

Before changing a debugging session status to ✅ RESOLVED, verify ALL applicable items:

### 1. Basic Proxy Health
- [ ] Proxy server starts without errors: `python proxy_server.py --config config.json`
- [ ] Health endpoint responds: `curl http://127.0.0.1:3001/health`
- [ ] Models endpoint responds: `curl http://127.0.0.1:3001/v1/models`

### 2. API Endpoint Tests
- [ ] OpenAI-compatible endpoint works: `python test_gpt.py` (if GPT models configured)
- [ ] Claude endpoint works: `python test_sonnet.py` (if Claude models configured)
- [ ] Messages API works: Test `/v1/messages` endpoint directly

### 3. Claude Code Integration Test (REQUIRED)
- [ ] **HTTP test passes**: `python test_claude_code_integration.py --http-only`
- [ ] **Full integration test passes**: `python test_claude_code_integration.py`

This test validates:
- Proxy can handle real Claude Code workloads
- Response streaming works correctly
- Token authentication works
- API format conversion is correct

### 4. Issue-Specific Verification
- [ ] The specific error from the debugging session no longer occurs
- [ ] Related functionality still works (no regression)
- [ ] Edge cases have been considered

### 5. Documentation Updated
- [ ] Debugging session file updated with verification results
- [ ] Test output saved (optional): `python test_claude_code_integration.py --save-output`

---

## Quick Verification Command

Run this single command to perform basic verification:

```bash
python test_claude_code_integration.py --http-only --save-output
```

For full verification including Claude CLI:

```bash
python test_claude_code_integration.py --save-output
```

---

## Test Output Location

Integration test outputs are saved to:
```
logs/integration_tests/integration_test_[type]_[timestamp].md
```

---

## When to Skip Tests

Some tests may be skipped in specific circumstances:

| Test | Can Skip If... |
|------|---------------|
| `test_gpt.py` | No GPT models configured in proxy |
| `test_sonnet.py` | No Claude models configured in proxy |
| CLI test | Claude CLI not installed (use `--http-only`) |

**However**, the HTTP integration test (`--http-only`) should NEVER be skipped for proxy fixes.

---

## Example Verification Session

```powershell
# 1. Start the proxy
python proxy_server.py --config config.json --debug

# 2. In another terminal, run verification
python test_claude_code_integration.py --http-only --save-output

# 3. Check results
# Expected output:
# ======================================================================
# 🧪 SAP AI Core LLM Proxy - Claude Code Integration Test
# ======================================================================
# 📥 Fetching latest changes from GitHub...
# 📊 Sync Status:
#    Last sync: abc12345...
#    Current:   def67890...
#    Origin:    def67890...
# 
# 🔌 Testing HTTP endpoint (/v1/messages)...
# ✅ HTTP test PASSED - received response from proxy
# 
# ======================================================================
# 📋 Test Results Summary
# ======================================================================
#    HTTP   : ✅ PASSED
# 
# ✅ Updated sync marker to: def67890...
# 
# ======================================================================
# 🎉 ALL TESTS PASSED - Proxy is functioning correctly!
# ======================================================================
```

---

## Failure Handling

If tests fail:

1. **Do NOT mark the issue as RESOLVED**
2. Review the error message in test output
3. Check proxy logs: `logs/` directory or terminal output
4. Update the debugging session with failure details
5. Continue investigation

---

## For AI Assistants

When debugging proxy issues:

1. **Always run the integration test** before claiming resolution
2. Include test results in the debugging session file
3. Use `--save-output` to preserve evidence
4. If test fails, the issue is NOT resolved - continue debugging