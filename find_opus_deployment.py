#!/usr/bin/env python3
"""
Script to find the deployment for Claude 4.5 Opus configuration.
"""
import json
import base64
import requests
from typing import Dict, Any, List


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


def list_configurations(service_key: Dict[str, Any], token: str, resource_group: str) -> List[Dict]:
    """List all configurations."""
    base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
    configs_url = f"{base_url}/v2/lm/configurations"

    headers = {
        "Authorization": f"Bearer {token}",
        "AI-Resource-Group": resource_group
    }

    response = requests.get(configs_url, headers=headers)
    response.raise_for_status()
    return response.json().get('resources', [])


def list_deployments(service_key: Dict[str, Any], token: str, resource_group: str) -> List[Dict]:
    """List all deployments."""
    base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
    deployments_url = f"{base_url}/v2/lm/deployments"

    headers = {
        "Authorization": f"Bearer {token}",
        "AI-Resource-Group": resource_group
    }

    response = requests.get(deployments_url, headers=headers)
    response.raise_for_status()
    return response.json().get('resources', [])


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
    base_url = service_key.get('serviceurls', {}).get('AI_API_URL')

    print("="*80)
    print("FINDING CLAUDE 4.5 OPUS DEPLOYMENT")
    print("="*80)

    # Get all configurations
    print("\n1. Fetching configurations...")
    configurations = list_configurations(service_key, token, resource_group)

    # Find Claude 4.5 Opus configurations
    opus_configs = []
    for config in configurations:
        config_name = config.get('name', '').lower()
        if 'claude-4.5-opus' in config_name or 'claude45_opus' in config_name:
            opus_configs.append({
                'id': config.get('id'),
                'name': config.get('name')
            })

    print(f"   Found {len(opus_configs)} Claude 4.5 Opus configuration(s)")

    # Get all deployments
    print("\n2. Fetching deployments...")
    deployments = list_deployments(service_key, token, resource_group)
    print(f"   Found {len(deployments)} total deployment(s)")

    # Match deployments to Opus configurations
    print("\n3. Matching deployments to Claude 4.5 Opus configurations...")
    opus_deployments = []

    for deployment in deployments:
        deployment_config_id = deployment.get('configurationId')
        deployment_status = deployment.get('status')

        # Check if this deployment is from an Opus configuration
        for opus_config in opus_configs:
            if opus_config['id'] == deployment_config_id:
                deployment_id = deployment.get('id')
                deployment_url = f"{base_url}/v2/inference/deployments/{deployment_id}"

                opus_deployments.append({
                    'deployment_id': deployment_id,
                    'deployment_url': deployment_url,
                    'status': deployment_status,
                    'config_name': opus_config['name'],
                    'config_id': opus_config['id']
                })

    # Print results
    print("\n" + "="*80)
    print("CLAUDE 4.5 OPUS DEPLOYMENTS FOUND:")
    print("="*80)

    if opus_deployments:
        running_deployments = [d for d in opus_deployments if d['status'] == 'RUNNING']

        if running_deployments:
            print(f"\n✓ Found {len(running_deployments)} RUNNING Claude 4.5 Opus deployment(s):")
            for dep in running_deployments:
                print(f"\n  Configuration: {dep['config_name']}")
                print(f"  Deployment ID: {dep['deployment_id']}")
                print(f"  Status: {dep['status']}")
                print(f"  URL: {dep['deployment_url']}")

            print("\n" + "="*80)
            print("ADD TO CONFIG.JSON:")
            print("="*80)
            print("""
Add these lines to the "deployment_models" section in config.json:
""")
            for dep in running_deployments[:1]:  # Show first one as example
                print(f'''    "claude-4.5-opus": [
        "{dep['deployment_url']}"
    ],
    "anthropic--claude-4.5-opus": [
        "{dep['deployment_url']}"
    ],''')

        else:
            print(f"\n⚠ Found {len(opus_deployments)} Claude 4.5 Opus deployment(s), but none are RUNNING:")
            for dep in opus_deployments:
                print(f"\n  Configuration: {dep['config_name']}")
                print(f"  Deployment ID: {dep['deployment_id']}")
                print(f"  Status: {dep['status']}")

            print("\n" + "="*80)
            print("ACTION NEEDED:")
            print("="*80)
            print("1. Go to SAP AI Core Launchpad or BTP Cockpit")
            print("2. Navigate to ML Operations -> Deployments")
            print("3. Start or create a deployment for one of the Claude 4.5 Opus configurations")
            print("4. Then run this script again to get the deployment URL")

    else:
        print("\n✗ No Claude 4.5 Opus deployments found.")
        print("\nAvailable Claude 4.5 Opus configurations that can be deployed:")
        for config in opus_configs:
            print(f"  - {config['name']} ({config['id']})")

        print("\n" + "="*80)
        print("ACTION NEEDED:")
        print("="*80)
        print("1. Go to SAP AI Core Launchpad or BTP Cockpit")
        print("2. Navigate to ML Operations -> Deployments")
        print("3. Click 'Create' to create a new deployment")
        print("4. Select one of the Claude 4.5 Opus configurations listed above")
        print("5. Start the deployment")
        print("6. Run this script again to get the deployment URL")


if __name__ == "__main__":
    main()
