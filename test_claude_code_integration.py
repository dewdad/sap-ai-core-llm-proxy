#!/usr/bin/env python3
"""
Claude Code Integration Test for SAP AI Core LLM Proxy

This script tests the proxy by:
1. Fetching latest changes from GitHub
2. Launching Claude Code to review recent changes
3. Verifying the proxy successfully handles the request

Usage:
    python test_claude_code_integration.py [--http-only] [--cli-only] [--save-output]

This test MUST pass before claiming any proxy issue is RESOLVED.
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import requests

# Configuration
PROXY_URL = "http://127.0.0.1:4337"
MESSAGES_ENDPOINT = f"{PROXY_URL}/v1/messages"
LAST_SYNC_FILE = ".last_sync_hash"
OUTPUT_DIR = "logs/integration_tests"


def get_auth_token():
    """Get authentication token from config or environment."""
    # Try environment variable first
    token = os.environ.get("ANTHROPIC_AUTH_TOKEN")
    if token:
        return token
    
    # Try config.json
    config_path = Path("config.json")
    if config_path.exists():
        with open(config_path) as f:
            config = json.load(f)
            tokens = config.get("secret_authentication_tokens", [])
            if tokens:
                return tokens[0]
    
    return "sk-my-secret-key-123"  # Default fallback


def get_last_sync_hash():
    """Get the last sync hash from marker file."""
    sync_file = Path(LAST_SYNC_FILE)
    if sync_file.exists():
        return sync_file.read_text().strip()
    return None


def save_last_sync_hash(commit_hash):
    """Save the current sync hash to marker file."""
    Path(LAST_SYNC_FILE).write_text(commit_hash)


def git_fetch():
    """Fetch latest changes from origin."""
    print("📥 Fetching latest changes from GitHub...")
    result = subprocess.run(
        ["git", "fetch", "origin"],
        capture_output=True,
        text=True
    )
    if result.returncode != 0:
        print(f"⚠️  Git fetch warning: {result.stderr}")
    return result.returncode == 0


def get_current_hash():
    """Get current HEAD commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def get_origin_hash():
    """Get origin/main commit hash."""
    result = subprocess.run(
        ["git", "rev-parse", "origin/main"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip() if result.returncode == 0 else None


def get_recent_commits(since_hash=None, limit=10):
    """Get recent commit messages for context."""
    if since_hash:
        cmd = ["git", "log", f"{since_hash}..HEAD", "--oneline", f"-{limit}"]
    else:
        cmd = ["git", "log", "--oneline", f"-{limit}"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def get_changed_files(since_hash=None):
    """Get list of changed files since last sync."""
    if since_hash:
        cmd = ["git", "diff", "--name-only", since_hash, "HEAD"]
    else:
        cmd = ["git", "diff", "--name-only", "HEAD~5", "HEAD"]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def test_http_endpoint(prompt, save_output=False):
    """
    Test the proxy via HTTP /v1/messages endpoint.
    
    Returns:
        tuple: (success: bool, response_text: str, error: str)
    """
    print("\n🔌 Testing HTTP endpoint (/v1/messages)...")
    
    headers = {
        "Content-Type": "application/json",
        "x-api-key": get_auth_token(),
        "anthropic-version": "2023-06-01"
    }
    
    data = {
        "model": "anthropic--claude-4-sonnet",
        "max_tokens": 2000,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }
    
    try:
        response = requests.post(
            MESSAGES_ENDPOINT,
            headers=headers,
            json=data,
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            content = ""
            
            # Extract text from response
            if "content" in result:
                for block in result["content"]:
                    if block.get("type") == "text":
                        content += block.get("text", "")
            
            if content:
                print("✅ HTTP test PASSED - received response from proxy")
                if save_output:
                    save_test_output("http", content)
                return True, content, None
            else:
                return False, "", "Empty response content"
        else:
            return False, "", f"HTTP {response.status_code}: {response.text[:200]}"
            
    except requests.exceptions.ConnectionError:
        return False, "", "Connection refused - is the proxy running?"
    except requests.exceptions.Timeout:
        return False, "", "Request timed out after 120s"
    except Exception as e:
        return False, "", str(e)


def test_claude_cli(prompt, save_output=False):
    """
    Test the proxy via Claude Code CLI.
    
    Returns:
        tuple: (success: bool, response_text: str, error: str)
    """
    print("\n🖥️  Testing Claude Code CLI...")
    
    # Check if claude CLI is available
    which_result = subprocess.run(
        ["where" if sys.platform == "win32" else "which", "claude"],
        capture_output=True,
        text=True
    )
    
    if which_result.returncode != 0:
        return False, "", "Claude CLI not found in PATH"
    
    # Set up environment for Claude to use the proxy
    env = os.environ.copy()
    env["ANTHROPIC_BASE_URL"] = PROXY_URL
    env["ANTHROPIC_AUTH_TOKEN"] = get_auth_token()
    env["ANTHROPIC_MODEL"] = "anthropic--claude-4-sonnet"
    
    try:
        # Run claude with --print flag for non-interactive mode
        result = subprocess.run(
            ["claude", "--print", prompt],
            capture_output=True,
            text=True,
            timeout=180,
            env=env
        )
        
        if result.returncode == 0 and result.stdout.strip():
            print("✅ CLI test PASSED - received response from Claude Code")
            content = result.stdout.strip()
            if save_output:
                save_test_output("cli", content)
            return True, content, None
        else:
            error = result.stderr.strip() if result.stderr else "No output received"
            return False, "", error
            
    except subprocess.TimeoutExpired:
        return False, "", "Claude CLI timed out after 180s"
    except Exception as e:
        return False, "", str(e)


def save_test_output(test_type, content):
    """Save test output to file for review."""
    output_dir = Path(OUTPUT_DIR)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = output_dir / f"integration_test_{test_type}_{timestamp}.md"
    
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"# Integration Test Output ({test_type.upper()})\n\n")
        f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
        f.write("## Response\n\n")
        f.write(content)
    
    print(f"📝 Output saved to: {filename}")


def build_review_prompt(since_hash=None):
    """Build the prompt for reviewing recent changes."""
    commits = get_recent_commits(since_hash)
    changed_files = get_changed_files(since_hash)
    
    prompt = """You are reviewing recent changes to the sap-ai-core-llm-proxy repository.

## Recent Commits
```
{commits}
```

## Changed Files
```
{files}
```

Please provide:
1. A brief summary of the changes (2-3 sentences)
2. Key modifications by category (bug fixes, features, documentation)
3. Any potential concerns or areas that need attention

Keep your response concise but informative.""".format(
        commits=commits if commits else "No recent commits found",
        files=changed_files if changed_files else "No file changes detected"
    )
    
    return prompt


def run_integration_test(http_only=False, cli_only=False, save_output=False):
    """
    Run the full integration test.
    
    Returns:
        bool: True if all requested tests pass
    """
    print("=" * 70)
    print("🧪 SAP AI Core LLM Proxy - Claude Code Integration Test")
    print("=" * 70)
    
    # Step 1: Fetch latest changes
    git_fetch()
    
    # Step 2: Get sync status
    last_sync = get_last_sync_hash()
    current_hash = get_current_hash()
    origin_hash = get_origin_hash()
    
    print(f"\n📊 Sync Status:")
    print(f"   Last sync: {last_sync[:8] if last_sync else 'Never'}...")
    print(f"   Current:   {current_hash[:8] if current_hash else 'Unknown'}...")
    print(f"   Origin:    {origin_hash[:8] if origin_hash else 'Unknown'}...")
    
    # Step 3: Build review prompt
    prompt = build_review_prompt(last_sync)
    
    # Step 4: Run tests
    results = {}
    
    if not cli_only:
        http_success, http_response, http_error = test_http_endpoint(prompt, save_output)
        results["http"] = {
            "success": http_success,
            "error": http_error
        }
        if not http_success:
            print(f"❌ HTTP test FAILED: {http_error}")
    
    if not http_only:
        cli_success, cli_response, cli_error = test_claude_cli(prompt, save_output)
        results["cli"] = {
            "success": cli_success,
            "error": cli_error
        }
        if not cli_success:
            print(f"❌ CLI test FAILED: {cli_error}")
    
    # Step 5: Summary
    print("\n" + "=" * 70)
    print("📋 Test Results Summary")
    print("=" * 70)
    
    all_passed = True
    for test_name, result in results.items():
        status = "✅ PASSED" if result["success"] else f"❌ FAILED: {result['error']}"
        print(f"   {test_name.upper():6} : {status}")
        if not result["success"]:
            all_passed = False
    
    # Step 6: Update sync marker on success
    if all_passed and current_hash:
        save_last_sync_hash(current_hash)
        print(f"\n✅ Updated sync marker to: {current_hash[:8]}...")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL TESTS PASSED - Proxy is functioning correctly!")
    else:
        print("⚠️  SOME TESTS FAILED - Proxy may have issues!")
    print("=" * 70)
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(
        description="Test Claude Code integration with SAP AI Core LLM Proxy"
    )
    parser.add_argument(
        "--http-only",
        action="store_true",
        help="Only test HTTP endpoint (skip CLI test)"
    )
    parser.add_argument(
        "--cli-only",
        action="store_true",
        help="Only test Claude CLI (skip HTTP test)"
    )
    parser.add_argument(
        "--save-output",
        action="store_true",
        help="Save test outputs to files for review"
    )
    
    args = parser.parse_args()
    
    success = run_integration_test(
        http_only=args.http_only,
        cli_only=args.cli_only,
        save_output=args.save_output
    )
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()