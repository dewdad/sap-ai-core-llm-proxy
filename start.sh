#!/bin/bash

# SAP AI Core LLM Proxy Startup Script
# This script activates the virtual environment and starts the proxy server

cd "$(dirname "$0")"

# Activate virtual environment
source .venv/bin/activate

# Start the proxy server
echo "Starting SAP AI Core LLM Proxy on http://127.0.0.1:4337"
echo "Press Ctrl+C to stop the server"
echo ""

python proxy_server.py --config config.json
