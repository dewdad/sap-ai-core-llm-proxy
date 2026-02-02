# SAP AI Core LLM Proxy Server Runner
# This script activates the virtual environment and starts the proxy server

param(
    [string]$Config = "config.json",
    [switch]$Debug
)

# Colors for output
$InfoColor = "Cyan"
$ErrorColor = "Red"
$SuccessColor = "Green"

# Set debug mode
$DebugMode = $Debug

# Check if config file exists
if (-not (Test-Path $Config)) {
    Write-Host "Error: Configuration file '$Config' not found!" -ForegroundColor $ErrorColor
    Write-Host "Please create a config.json file from config.json.example" -ForegroundColor $InfoColor
    Write-Host "Example: Copy-Item config.json.example config.json" -ForegroundColor $InfoColor
    exit 1
}

# Activate virtual environment
$VenvActivate = ".\.venv\Scripts\Activate.ps1"

if (-not (Test-Path $VenvActivate)) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor $ErrorColor
    Write-Host "Please run 'uv venv' to create a virtual environment first." -ForegroundColor $InfoColor
    exit 1
}

Write-Host "Activating virtual environment..." -ForegroundColor $InfoColor
& $VenvActivate

# Build command
$Command = "python proxy_server.py --config $Config"
if ($DebugMode) {
    $Command += " --debug"
}

# Start the proxy server
Write-Host "Starting SAP AI Core LLM Proxy Server..." -ForegroundColor $SuccessColor
Write-Host "Configuration: $Config" -ForegroundColor $InfoColor
if ($DebugMode) {
    Write-Host "Debug mode: enabled" -ForegroundColor $InfoColor
}
Write-Host ""

Invoke-Expression $Command
