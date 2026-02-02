# Debugging Session: SAP AI SDK Authentication Failure

**Date:** 2026-02-02  
**Issue ID:** SDK-AUTH-001  
**Status:** ✅ RESOLVED  
**Severity:** Critical - Claude Code integration completely broken

## Problem Summary

Claude Code was unable to connect to the proxy server. All requests to `/v1/messages` endpoint failed with authentication errors.

## Error Signature

```
ERROR - Error handling Anthropic proxy request using SDK: Could not retrieve Authorization token:
For authorization please provide either one of the following options:
1. token_creator
2. auth_url, client_id and one of the following options:
    a. client_secret
    b. cert_str & key_str
    c. cert_file_path & key_file_path
```

### Stack Trace Pattern
```
ai_api_client_sdk.ai_api_v2_client.py -> _create_token_creator_if_does_not_exist
ai_api_client_sdk.helpers.authenticator.py -> __init__
ai_api_client_sdk.exception.AIAPIAuthenticatorException: Could not retrieve Authorization token
```

## Root Cause Analysis

### Investigation Steps

1. **Error Analysis:** The SDK (`gen_ai_hub` → `ai_core_sdk`) uses `AICoreV2Client.from_env()` to initialize, which expects authentication credentials from:
   - Environment variables (`AICORE_AUTH_URL`, `AICORE_CLIENT_ID`, `AICORE_CLIENT_SECRET`)
   - Config file at `~/.aicore/config.json`

2. **Config File Check:** Verified `~/.aicore/config.json` does NOT exist on the system:
   ```powershell
   Get-Content $env:USERPROFILE\.aicore\config.json
   # Result: File does not exist at C:\Users\avita_n145\.aicore\config.json
   ```

3. **Code Review:** The existing monkey patch in `proxy_server.py` (lines 70-97) only injected `base_url` but NOT the authentication credentials (`auth_url`, `client_id`, `client_secret`).

### Root Cause
The monkey patch `_patched_from_env()` was incomplete - it handled `base_url` injection but did not inject the required authentication parameters that the SDK needs to create its token authenticator.

## Solution Applied

### Changes to `proxy_server.py`

1. **Added new function `_extract_auth_credentials_from_proxy_config()`** (lines 63-81):
   ```python
   def _extract_auth_credentials_from_proxy_config():
       """Extract authentication credentials from proxy configuration service keys."""
       global _extracted_auth_credentials
       
       if _extracted_auth_credentials:
           return _extracted_auth_credentials
       
       try:
           # Get credentials from the first available subaccount's service key
           for subaccount in proxy_config.subaccounts.values():
               if subaccount.service_key:
                   _extracted_auth_credentials = {
                       'auth_url': subaccount.service_key.url,
                       'client_id': subaccount.service_key.clientid,
                       'client_secret': subaccount.service_key.clientsecret
                   }
                   logging.info(f"Extracted auth credentials from subaccount '{subaccount.name}' service key")
                   return _extracted_auth_credentials
       except Exception as e:
           logging.debug(f"Could not extract auth credentials from proxy config: {e}")
       
       return None
   ```

2. **Enhanced `_patched_from_env()` function** (lines 83-152) to inject authentication credentials:
   - Added logic to inject `auth_url`, `client_id`, `client_secret` from proxy config
   - Added fallback to `~/.aicore/config.json` for these parameters
   - Added warning logs when credentials are missing

### Credential Mapping
| Service Key Field | SDK Parameter | Source |
|-------------------|---------------|--------|
| `service_key.url` | `auth_url` | OAuth token endpoint base URL |
| `service_key.clientid` | `client_id` | OAuth client ID |
| `service_key.clientsecret` | `client_secret` | OAuth client secret |

## Verification

After applying the fix:
1. Restart the proxy server
2. The SDK will receive authentication credentials from the existing service key configuration in `config.json`
3. No additional configuration files (`~/.aicore/config.json`) are needed

## Related Files

- `proxy_server.py` - Main proxy server with monkey patch fix
- `config.json` - Proxy configuration containing service keys
- Service key JSON files (referenced in config.json)

## Prevention Recommendations

1. **Documentation:** Update AGENTS.md to note that the SDK authentication relies on the monkey patch
2. **Testing:** Add integration test that verifies SDK client initialization
3. **Logging:** The fix includes enhanced logging that will help diagnose similar issues faster

## Keywords/Tags

`sdk-authentication`, `AICoreV2Client`, `gen_ai_hub`, `ai_core_sdk`, `monkey-patch`, `service-key`, `oauth`, `claude-code`, `/v1/messages`