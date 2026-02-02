#!/usr/bin/env python3
"""
Script to list all deployments from SAP AI Core.
This helps discover deployment URLs for models like Claude 4.5 Opus.
"""
import json
import base64
import requests
import sys
from typing import Dict, Any


def load_service_key(key_file: str = "key.json") -> Dict[str, Any]:
    """Load SAP AI Core service key from file."""
    try:
        with open(key_file, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {key_file} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: {key_file} is not valid JSON")
        sys.exit(1)


def get_token(service_key: Dict[str, Any]) -> str:
    """Get authentication token from SAP AI Core."""
    client_id = service_key.get('clientid')
    client_secret = service_key.get('clientsecret')
    auth_url = service_key.get('url')

    if not all([client_id, client_secret, auth_url]):
        print("Error: Missing required fields in service key")
        sys.exit(1)

    # Encode credentials
    auth_string = f"{client_id}:{client_secret}"
    encoded_auth = base64.b64encode(auth_string.encode()).decode()

    # Request token
    token_url = f"{auth_url}/oauth/token?grant_type=client_credentials"
    headers = {"Authorization": f"Basic {encoded_auth}"}

    try:
        response = requests.post(token_url, headers=headers)
        response.raise_for_status()
        return response.json()['access_token']
    except requests.RequestException as e:
        print(f"Error getting token: {e}")
        sys.exit(1)


def get_deployment_details(service_key: Dict[str, Any], token: str, deployment_id: str, resource_group: str = "default") -> Dict[str, Any]:
    """Get detailed configuration for a specific deployment."""
    base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
    deployment_url = f"{base_url}/v2/lm/deployments/{deployment_id}"
    headers = {
        "Authorization": f"Bearer {token}",
        "AI-Resource-Group": resource_group
    }

    try:
        response = requests.get(deployment_url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return {}


def list_deployments(service_key: Dict[str, Any], token: str, resource_group: str = "default") -> list:
    """List all deployments from SAP AI Core."""
    base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
    if not base_url:
        print("Error: AI_API_URL not found in service key")
        sys.exit(1)

    # Query deployments
    deployments_url = f"{base_url}/v2/lm/deployments"
    headers = {
        "Authorization": f"Bearer {token}",
        "AI-Resource-Group": resource_group
    }

    try:
        response = requests.get(deployments_url, headers=headers)
        response.raise_for_status()
        return response.json().get('resources', [])
    except requests.RequestException as e:
        print(f"Error listing deployments: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        sys.exit(1)


def main():
    # Load configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
    except FileNotFoundError:
        print("Error: config.json not found")
        sys.exit(1)

    # Get first subaccount config
    subaccounts = config.get('subAccounts', {})
    if not subaccounts:
        print("Error: No subaccounts configured")
        sys.exit(1)

    for subaccount_name, subaccount_config in subaccounts.items():
        print(f"\n{'='*80}")
        print(f"SubAccount: {subaccount_name}")
        print(f"{'='*80}")

        resource_group = subaccount_config.get('resource_group', 'default')
        key_file = subaccount_config.get('service_key_json', 'key.json')

        # Load service key and get token
        service_key = load_service_key(key_file)
        token = get_token(service_key)

        # List deployments
        deployments = list_deployments(service_key, token, resource_group)

        print(f"\nFound {len(deployments)} deployment(s) in resource group '{resource_group}':")
        print()

        # Group deployments by model
        claude_deployments = []
        other_deployments = []

        print("Fetching deployment details (this may take a moment)...")
        for i, deployment in enumerate(deployments):
            if i % 20 == 0:
                print(f"  Processed {i}/{len(deployments)} deployments...")

            deployment_id = deployment.get('id')
            status = deployment.get('status')

            # Skip non-running deployments to save time
            if status != 'RUNNING':
                continue

            # Get detailed deployment info
            details = get_deployment_details(service_key, token, deployment_id, resource_group)

            # Extract model name from configuration parameters
            model_name = "unknown"
            config_params = details.get('configurationId', '')

            # Try to get model from details
            if 'details' in details and 'resources' in details['details']:
                resources = details['details']['resources']
                if 'backend_details' in resources:
                    backend = resources['backend_details']
                    if 'model' in backend:
                        model_name = backend['model']['name']

            # Fallback: try configuration name
            if model_name == "unknown":
                config_name = details.get('configurationName', '')
                if config_name:
                    model_name = config_name

            # Get deployment URL
            base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
            deployment_url = f"{base_url}/v2/inference/deployments/{deployment_id}"

            deployment_info = {
                'id': deployment_id,
                'url': deployment_url,
                'status': status,
                'model': model_name,
                'config': config_params
            }

            if 'claude' in model_name.lower() or 'anthropic' in model_name.lower() or 'opus' in model_name.lower():
                claude_deployments.append(deployment_info)
            elif model_name != "unknown":
                other_deployments.append(deployment_info)

        print(f"  Completed processing {len(deployments)} deployments.")

        # Print Claude deployments first
        if claude_deployments:
            print("\n" + "="*80)
            print("CLAUDE / ANTHROPIC MODELS FOUND:")
            print("="*80)
            for dep in claude_deployments:
                print(f"\n  Model: {dep['model']}")
                print(f"  Status: {dep['status']}")
                print(f"  Config: {dep['config']}")
                print(f"  URL: {dep['url']}")
        else:
            print("\nNo Claude/Anthropic models found in RUNNING status.")

        # Print sample of other deployments
        if other_deployments:
            print("\n" + "="*80)
            print(f"OTHER MODELS (showing first 10 of {len(other_deployments)}):")
            print("="*80)
            for dep in other_deployments[:10]:
                print(f"\n  Model: {dep['model']}")
                print(f"  Status: {dep['status']}")
                print(f"  URL: {dep['url']}")

    print("\n" + "="*80)
    print("To add a model to config.json, copy the deployment URL and add it like this:")
    print("="*80)
    print("""
    "deployment_models": {
        "claude-4.5-opus": [
            "https://api.ai....../v2/inference/deployments/dXXXXXXX"
        ],
        "anthropic--claude-4.5-opus": [
            "https://api.ai....../v2/inference/deployments/dXXXXXXX"
        ]
    }
    """)


if __name__ == "__main__":
    main()
