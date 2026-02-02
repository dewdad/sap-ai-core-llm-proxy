#!/usr/bin/env python3
"""
Script to list all configurations from SAP AI Core.
This shows what models can be deployed.
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


def list_configurations(service_key: Dict[str, Any], token: str, resource_group: str) -> list:
    """List all configurations from SAP AI Core."""
    base_url = service_key.get('serviceurls', {}).get('AI_API_URL')
    configs_url = f"{base_url}/v2/lm/configurations"

    headers = {
        "Authorization": f"Bearer {token}",
        "AI-Resource-Group": resource_group
    }

    try:
        response = requests.get(configs_url, headers=headers)
        response.raise_for_status()
        return response.json().get('resources', [])
    except requests.RequestException as e:
        print(f"Error listing configurations: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []


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

    # List configurations
    configurations = list_configurations(service_key, token, resource_group)

    print("="*80)
    print(f"Found {len(configurations)} configuration(s)")
    print("="*80)

    # Group by model type
    claude_configs = []
    other_configs = []

    for config in configurations:
        config_id = config.get('id', '')
        config_name = config.get('name', '')
        scenario_id = config.get('scenarioId', '')

        # Get parameters to find model name
        params = config.get('inputArtifactBindings', [])

        config_info = {
            'id': config_id,
            'name': config_name,
            'scenario': scenario_id,
            'params': params
        }

        if 'claude' in config_name.lower() or 'anthropic' in config_name.lower() or 'opus' in config_name.lower():
            claude_configs.append(config_info)
        else:
            other_configs.append(config_info)

    # Print Claude configurations
    if claude_configs:
        print("\n" + "="*80)
        print("CLAUDE / ANTHROPIC CONFIGURATIONS:")
        print("="*80)
        for cfg in claude_configs:
            print(f"\n  Name: {cfg['name']}")
            print(f"  ID: {cfg['id']}")
            print(f"  Scenario: {cfg['scenario']}")
            if cfg['params']:
                print(f"  Parameters: {json.dumps(cfg['params'], indent=4)}")
    else:
        print("\nNo Claude/Anthropic configurations found.")

    # Print sample of other configurations
    if other_configs and len(other_configs) <= 20:
        print("\n" + "="*80)
        print(f"OTHER CONFIGURATIONS ({len(other_configs)}):")
        print("="*80)
        for cfg in other_configs[:20]:
            print(f"\n  Name: {cfg['name']}")
            print(f"  ID: {cfg['id']}")

    print("\n" + "="*80)
    print("To deploy a configuration and get its deployment ID:")
    print("="*80)
    print("1. Use the SAP AI Core Launchpad or BTP cockpit")
    print("2. Navigate to ML Operations -> Deployments")
    print("3. Create a new deployment from the configuration")
    print("4. Copy the deployment ID and add to config.json")


if __name__ == "__main__":
    main()
