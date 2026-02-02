#!/usr/bin/env python3
"""
Script to test a specific deployment to identify which model it serves.
"""
import json
import base64
import requests
import sys
from typing import Dict, Any


def load_service_key(key_file: str = "key.json") -> Dict[str, Any]:
    """Load SAP AI Core service key from file."""
    with open(key_file, 'r') as f:
        return json.load(f)


def get_token(service_key: Dict[str, Any]) -> str:
    """Get authentication token from SAP AI Core."""
    client_id = service_key.get('clientid')
    client_secret = service_key.get('clientsecret')
    auth_url = service_key.get('url')

    auth_string = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    token_url = f"{auth_url}/oauth/token?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {encoded_auth}"}

    response = requests.post(token_url, headers=headers)
    response.raise_for_status()
    return response.json()['access_token']


def test_deployment(service_key: Dict[str, Any], token: str, deployment_id: str, resource_group: str) -> Dict[str, Any]:
    """Test a deployment by sending a simple request."""
    base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
    deployment_url = f"{base_url}/v2/inference/deployments/{deployment_id}"

    headers = {
        "Authorization": f"Bearer {token}",
        "AI-Resource-Group": resource_group,
        "Content-Type": "application/json"
    }

    # Send a test message to identify the model
    payload = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 10,
        "messages": [
            {
                "role": "user",
                "content": "Say 'test'"
            }
        ]
    }

    try:
        print(f"\n  Testing deployment {deployment_id}...")
        response = requests.post(deployment_url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            result = response.json()
            # Try to extract model info from response headers or body
            model_header = response.headers.get('x-model-id', 'unknown')
            return {
                'success': True,
                'status_code': response.status_code,
                'model_header': model_header,
                'response': result
            }
        else:
            return {
                'success': False,
                'status_code': response.status_code,
                'error': response.text
            }
    except requests.Timeout:
        return {'success': False, 'error': 'Request timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def main():
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)

    subaccount_config = config['subAccounts']['main']
    resource_group = subaccount_config['resource_group']
    key_file = subaccount_config.get('service_key_json', 'key.json')

    # Load service key and get token
    service_key = load_service_key(key_file)
    token = get_token(service_key)

    print("="*80)
    print("TESTING CLAUDE DEPLOYMENTS")
    print("="*80)

    # Test known Claude deployments from config.json
    known_deployments = {
        'Claude 4.5 Sonnet (known)': 'd0c56b8d3578bd1b',
        'Claude 4.5 Haiku (known)': 'dfe7874938d2c0f6',
    }

    # Test a few deployment IDs that might be Claude 4.5 Opus
    # Looking for patterns similar to existing Claude deployments
    potential_opus_deployments = {
        'Potential Opus 1': 'd635d2e4e4023c3e',
        'Potential Opus 2': 'd3d5b1c3ec655230',
        'Potential Opus 3': 'dda818db4a6ebeaa',
        'Potential Opus 4': 'df4b4ef707c98fec',
        'Potential Opus 5': 'd14636a118a96e18',
    }

    # Test known deployments first
    print("\nKnown Claude Deployments:")
    print("-" * 80)
    for name, deployment_id in known_deployments.items():
        result = test_deployment(service_key, token, deployment_id, resource_group)
        print(f"\n{name} ({deployment_id}):")
        if result['success']:
            print(f"  Status: SUCCESS")
            print(f"  Model Header: {result.get('model_header', 'N/A')}")
            if 'response' in result:
                content = result['response'].get('content', [])
                if content and len(content) > 0:
                    text = content[0].get('text', '')
                    print(f"  Response: {text}")
        else:
            print(f"  Status: FAILED - {result.get('error', 'Unknown error')}")

    # Test potential Opus deployments
    print("\n\nTesting Potential Claude 4.5 Opus Deployments:")
    print("-" * 80)
    for name, deployment_id in potential_opus_deployments.items():
        result = test_deployment(service_key, token, deployment_id, resource_group)
        print(f"\n{name} ({deployment_id}):")
        if result['success']:
            print(f"  Status: SUCCESS - This might be Claude 4.5 Opus!")
            print(f"  Model Header: {result.get('model_header', 'N/A')}")
            base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
            print(f"  URL: {base_url}/v2/inference/deployments/{deployment_id}")
        else:
            print(f"  Status: FAILED - {result.get('error', 'Unknown error')[:100]}")

    print("\n" + "="*80)
    print("If a deployment tested successfully, add it to config.json as:")
    print("="*80)
    print("""
    "claude-4.5-opus": [
        "https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dXXXXXXXXXXXXXXX"
    ],
    "anthropic--claude-4.5-opus": [
        "https://api.ai.prod.eu-central-1.aws.ml.hana.ondemand.com/v2/inference/deployments/dXXXXXXXXXXXXXXX"
    ]
    """)


if __name__ == "__main__":
    main()
