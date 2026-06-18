Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

python --version
git --version
ffmpeg -version | Select-Object -First 1

if (Test-Path ".venv\Scripts\python.exe") {
  .\.venv\Scripts\python.exe -m pip list
  .\.venv\Scripts\python.exe main.py --help
} else {
  python -m pip list
  python main.py --help
}

Write-Host "Laptop environment verification complete."
