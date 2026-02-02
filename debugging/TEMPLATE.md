# Debugging Session: [Brief Title]

**Date:** YYYY-MM-DD  
**Issue ID:** [CATEGORY]-[NUMBER] (e.g., SDK-AUTH-001, STREAM-001, CONFIG-001)  
**Status:** 🔴 INVESTIGATING | 🟡 IN PROGRESS | ✅ RESOLVED | ❌ WONTFIX  
**Severity:** Critical | High | Medium | Low

## Problem Summary

[1-2 sentences describing what the user/system experienced]

## Error Signature

```
[Paste the key error message here]
```

### Stack Trace Pattern (if applicable)
```
[Key parts of the stack trace that identify this issue]
```

## Root Cause Analysis

### Investigation Steps

1. **Step description:** [What was checked and what was found]
2. **Step description:** [What was checked and what was found]
3. ...

### Root Cause
[Clear explanation of what caused the issue]

## Solution Applied

### Changes Made

[Describe the changes, with code snippets if helpful]

```python
# Example code change
```

### Files Modified
- `filename.py` - [Brief description of changes]

## Verification

**REQUIRED**: Complete the [VERIFICATION_CHECKLIST.md](VERIFICATION_CHECKLIST.md) before marking as RESOLVED.

### Verification Steps Performed

1. [ ] Proxy server starts without errors
2. [ ] Health endpoint responds
3. [ ] Claude Code integration test passes: `python test_claude_code_integration.py --http-only`

### Integration Test Results

```
[Paste the output of: python test_claude_code_integration.py --http-only --save-output]
```

### Issue-Specific Verification

[Steps to verify the specific fix works]

## Related Files

- `file1.py` - [Why it's related]
- `file2.json` - [Why it's related]

## Prevention Recommendations

1. [Recommendation 1]
2. [Recommendation 2]

## Keywords/Tags

`keyword1`, `keyword2`, `keyword3`

---

## Session Notes (Optional)

[Any additional context, alternative approaches tried, or lessons learned]