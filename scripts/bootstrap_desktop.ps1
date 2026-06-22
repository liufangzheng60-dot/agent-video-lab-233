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
    Write-Host "AGENT_VIDEO_DATA_ROOT is not set; using local test data root: $DataRoot"
} else {
    Write-Host "Using AGENT_VIDEO_DATA_ROOT: $DataRoot"
}

$dirs = @(
    $DataRoot,
    (Join-Path $DataRoot "synthetic_smoke\inputs"),
    (Join-Path $DataRoot "synthetic_smoke\outputs"),
    (Join-Path $DataRoot "products\dog_stairs_v1\inputs"),
    (Join-Path $DataRoot "products\dog_stairs_v1\outputs")
)
foreach ($dir in $dirs) {
    New-Item -ItemType Directory -Force -Path $dir | Out-Null
}

foreach ($tool in @("python", "ffmpeg", "git")) {
    $cmd = Get-Command $tool -ErrorAction SilentlyContinue
    if (-not $cmd) {
        throw "$tool is required but was not found on PATH."
    }
    Write-Host "$tool found: $($cmd.Source)"
}

Write-Host "Bootstrap complete. No business videos were downloaded, copied, or moved."
Write-Host "Optional for this shell: `$env:AGENT_VIDEO_DATA_ROOT = '$DataRoot'"
