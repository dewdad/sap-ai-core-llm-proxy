#!/bin/bash

# Script to stop the proxy server running on the port defined in config.json

# Get the directory where the script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/config.json"

# Check if config.json exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: config.json not found at $CONFIG_FILE"
    exit 1
fi

# Extract port from config.json using Python
PORT=$(python3 -c "import json; print(json.load(open('$CONFIG_FILE'))['port'])" 2>/dev/null)

if [ -z "$PORT" ]; then
    echo "Error: Could not read port from config.json"
    exit 1
fi

echo "Looking for process on port $PORT..."

# Find the PID of the process using the port
PID=$(lsof -ti :$PORT)

if [ -z "$PID" ]; then
    echo "No process found running on port $PORT"
    exit 0
fi

echo "Found process $PID running on port $PORT"
echo "Stopping process..."

# Try graceful shutdown first (SIGTERM)
kill $PID 2>/dev/null

# Wait up to 5 seconds for the process to stop
for i in {1..5}; do
    sleep 1
    if ! kill -0 $PID 2>/dev/null; then
        echo "Process stopped successfully"
        exit 0
    fi
done

# If still running, force kill (SIGKILL)
echo "Process did not stop gracefully, forcing shutdown..."
kill -9 $PID 2>/dev/null

# Verify the process is stopped
if kill -0 $PID 2>/dev/null; then
    echo "Error: Failed to stop process $PID"
    exit 1
else
    echo "Process forcefully stopped"
    exit 0
fi
