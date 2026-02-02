#!/usr/bin/env python3
"""Test Claude 4.5 Opus through the proxy."""
import requests
import json

# Test OpenAI-compatible endpoint
print("="*80)
print("Testing Claude 4.5 Opus via OpenAI-compatible API")
print("="*80)

url = "http://127.0.0.1:4337/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-my-secret-key-123"
}
data = {
    "model": "claude-4.5-opus",
    "messages": [
        {"role": "user", "content": "Say 'Hello from Claude 4.5 Opus!'"}
    ],
    "max_tokens": 50
}

try:
    print(f"\nRequest URL: {url}")
    print(f"Request Model: {data['model']}")
    print(f"Request Message: {data['messages'][0]['content']}")
    print("\nSending request...")

    response = requests.post(url, headers=headers, json=data, timeout=20)

    print(f"\nResponse Status: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")

    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))

        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0].get('message', {}).get('content', '')
            print(f"\n✓ SUCCESS! Claude 4.5 Opus responded:")
            print(f"  {content}")
    else:
        print(response.text)
        print(f"\n✗ FAILED with status code {response.status_code}")

except requests.Timeout:
    print("\n✗ FAILED: Request timed out")
except Exception as e:
    print(f"\n✗ FAILED: {e}")

# Test Anthropic Messages API endpoint
print("\n" + "="*80)
print("Testing Claude 4.5 Opus via Anthropic Messages API")
print("="*80)

url = "http://127.0.0.1:4337/v1/messages"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-my-secret-key-123",
    "anthropic-version": "2023-06-01"
}
data = {
    "model": "claude-4.5-opus",
    "messages": [
        {"role": "user", "content": "Say 'Hello from Claude 4.5 Opus!'"}
    ],
    "max_tokens": 50
}

try:
    print(f"\nRequest URL: {url}")
    print(f"Request Model: {data['model']}")
    print(f"Request Message: {data['messages'][0]['content']}")
    print("\nSending request...")

    response = requests.post(url, headers=headers, json=data, timeout=20)

    print(f"\nResponse Status: {response.status_code}")
    print(f"\nResponse Body:")

    if response.status_code == 200:
        result = response.json()
        print(json.dumps(result, indent=2))

        if 'content' in result and len(result['content']) > 0:
            content = result['content'][0].get('text', '')
            print(f"\n✓ SUCCESS! Claude 4.5 Opus responded:")
            print(f"  {content}")
    else:
        print(response.text)
        print(f"\n✗ FAILED with status code {response.status_code}")

except requests.Timeout:
    print("\n✗ FAILED: Request timed out")
except Exception as e:
    print(f"\n✗ FAILED: {e}")
