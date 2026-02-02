#!/usr/bin/env python3
"""Test GPT model through the proxy."""
import requests
import json

print("="*80)
print("Testing GPT-4o")
print("="*80)

url = "http://127.0.0.1:4337/v1/chat/completions"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer sk-my-secret-key-123"
}
data = {
    "model": "gpt-4o",
    "messages": [
        {"role": "user", "content": "Say 'Hello from GPT-4o!'"}
    ],
    "max_tokens": 50
}

try:
    print(f"\nRequest Model: {data['model']}")
    print("Sending request...")

    response = requests.post(url, headers=headers, json=data, timeout=20)

    print(f"Response Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print("\nResponse:")
        print(json.dumps(result, indent=2))

        if 'choices' in result and len(result['choices']) > 0:
            content = result['choices'][0].get('message', {}).get('content', '')
            print(f"\n✓ SUCCESS! GPT-4o responded:")
            print(f"  {content}")
    else:
        print(f"\nResponse Body: {response.text}")
        print(f"\n✗ FAILED with status code {response.status_code}")

except Exception as e:
    print(f"\n✗ FAILED: {e}")
