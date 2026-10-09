# Creates a virtual environment (if needed) and installs backend dependencies.
# Run from the backend/ folder:  .\setup.ps1

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment in .venv ..."
    python -m venv .venv
} else {
    Write-Host ".venv already exists, reusing it."
}

Write-Host "Upgrading pip ..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip

Write-Host "Installing dependencies from requirements.txt ..."
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt

Write-Host ""
Write-Host "Done. Activate the environment with:"
Write-Host "    .\.venv\Scripts\Activate.ps1"