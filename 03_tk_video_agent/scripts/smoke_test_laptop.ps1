Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# This smoke test does not require raw videos. If full tests depend on local media,
# run the focused smoke subset first and run media tests only after copying assets.
if (Test-Path ".venv\Scripts\python.exe") {
  .\.venv\Scripts\python.exe main.py --help
  .\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*gitignore*.py"
  .\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*laptop*.py"
  .\.venv\Scripts\python.exe -m unittest discover -s tests -p "test_*p12_audit*.py"
} else {
  python main.py --help
  python -m unittest discover -s tests -p "test_*gitignore*.py"
  python -m unittest discover -s tests -p "test_*laptop*.py"
  python -m unittest discover -s tests -p "test_*p12_audit*.py"
}
