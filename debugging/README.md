# Debugging Sessions Repository

This folder contains documented debugging and repair sessions for the SAP AI Core LLM Proxy. Each session captures the problem, investigation process, root cause analysis, and solution applied.

## Purpose

- **Knowledge Preservation:** Capture solutions so they can be referenced when similar issues occur
- **Pattern Recognition:** Identify recurring issues by reviewing past sessions
- **Faster Resolution:** Reduce debugging time by checking if an issue has been solved before
- **Context for AI Assistants:** Provide debugging context to AI coding assistants

## How to Use

### When Debugging a New Issue

1. **Search first:** Check if a similar issue exists by searching keywords in existing sessions
2. **Create a new session:** Copy `TEMPLATE.md` and fill in the details as you investigate
3. **Name convention:** `YYYY-MM-DD_brief-description.md` (e.g., `2026-02-02_sdk-authentication-fix.md`)

### Session File Naming Convention

```
YYYY-MM-DD_category-brief-description.md
```

**Categories:**
- `sdk-` - SAP AI SDK related issues
- `auth-` - Authentication/authorization issues
- `stream-` - Streaming response issues
- `config-` - Configuration issues
- `api-` - API format/conversion issues
- `conn-` - Connection/networking issues
- `perf-` - Performance issues

### Issue ID Convention

```
[CATEGORY]-[NUMBER]
```

Examples:
- `SDK-AUTH-001` - First SDK authentication issue
- `STREAM-001` - First streaming issue
- `CONFIG-002` - Second configuration issue

## Searching Sessions

### By Error Message
Search for the key error text across all markdown files:
```powershell
# PowerShell
Get-ChildItem -Path debugging -Filter "*.md" | Select-String "error message text"
```

### By Keyword/Tag
Each session includes a Keywords/Tags section at the bottom for searchability.

### By Status
- 🔴 `INVESTIGATING` - Issue still being analyzed
- 🟡 `IN PROGRESS` - Solution identified, implementation in progress
- ✅ `RESOLVED` - Issue fixed and verified
- ❌ `WONTFIX` - Issue documented but not fixed (with explanation)

## Session Index

| Date | Issue ID | Title | Status |
|------|----------|-------|--------|
| 2026-02-02 | SDK-AUTH-001 | [SDK Authentication Failure](2026-02-02_sdk-authentication-fix.md) | ✅ RESOLVED |

---

## For AI Assistants

When debugging proxy issues, **always check this folder first** for relevant past sessions:

1. Read `README.md` to understand the structure
2. Review the session index above for potentially related issues
3. Search session files by error patterns or keywords
4. Reference applicable solutions in your debugging approach
5. **Create a new session file** when resolving new issues
6. **MANDATORY**: Run `python test_claude_code_integration.py --http-only` before marking any issue as RESOLVED
7. Complete the [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) before claiming resolution

### ⚠️ IMPORTANT: Verification Required

**DO NOT mark any debugging session as ✅ RESOLVED until:**
- The Claude Code integration test passes
- All items in [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) are checked
- Test output is included in the debugging session file

### Quick Reference - Common Issue Patterns

| Error Pattern | Likely Cause | Session Reference |
|--------------|--------------|-------------------|
| `Could not retrieve Authorization token` | SDK credentials not injected | SDK-AUTH-001 |
| `client_type parameter not accepted` | SDK version compatibility | Check monkey patch in proxy_server.py |
| `Connection pool exhausted` | Too many concurrent requests | Check connection pool settings |