param(
    [string]$DataRoot = $env:AGENT_VIDEO_DATA_ROOT
)

$ErrorActionPreference = "Stop"
$RepoRoot = (git rev-parse --show-toplevel 2>$null)
if (-not $RepoRoot) {
    $RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
}
if (-not $DataRoot) {
    $DataRoot = (Join-Path (Split-Path $RepoRoot -Parent) "agent_video_data_local")
}

Write-Host "Repository: $RepoRoot"
Write-Host "Data root: $DataRoot"
git -C $RepoRoot status --short

python --version
ffmpeg -version | Select-Object -First 1
git --version

$env:PYTHONPATH = Join-Path $RepoRoot "03_tk_video_agent"
$check = @'
import importlib.util
import cv2
print("opencv", cv2.__version__)
print("edge_tts", "ok" if importlib.util.find_spec("edge_tts") else "missing")
'@
$check | python -

if ($env:ZHIPU_API_KEY) {
    Write-Host "ZHIPU_API_KEY: present"
} else {
    Write-Host "ZHIPU_API_KEY: missing (VLM smoke test will be skipped unless enabled with a key)"
}

foreach ($dir in @($DataRoot, (Join-Path $DataRoot "synthetic_smoke\outputs"))) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
    $probe = Join-Path $dir ".write_probe"
    "ok" | Set-Content -Path $probe -Encoding UTF8
    Remove-Item -LiteralPath $probe -Force
    Write-Host "Writable: $dir"
}
