Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

Write-Host "Checking Python..."
python --version

Write-Host "Checking Git..."
git --version

Write-Host "Checking ffmpeg..."
ffmpeg -version | Select-Object -First 1

Write-Host "Creating virtual environment..."
if (!(Test-Path ".venv")) {
  python -m venv .venv
}

Write-Host "Installing Python dependencies..."
.\.venv\Scripts\python.exe -m pip install --upgrade pip
if (Test-Path "requirements.txt") {
  .\.venv\Scripts\python.exe -m pip install -r requirements.txt
} elseif (Test-Path "..\requirements.txt") {
  .\.venv\Scripts\python.exe -m pip install -r ..\requirements.txt
}

Write-Host "Copy .env.example to .env and fill local secrets manually. Do not commit .env."
