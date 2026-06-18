"""Media asset checks for P12 dry-run production."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


MEDIA_SUFFIXES = {".mp4", ".mov", ".avi", ".mkv", ".jpg", ".jpeg", ".png", ".webp", ".wav", ".mp3", ".xlsx"}


def _git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)


def _is_git_ignored(repo_root: Path, path: Path) -> bool:
    result = _git(repo_root, ["check-ignore", "-q", str(path)])
    if result.returncode == 0:
        return True
    child_result = _git(repo_root, ["check-ignore", "-q", str(path / "__guard_probe__")])
    return child_result.returncode == 0


def _tracked_files(repo_root: Path) -> list[str]:
    result = _git(repo_root, ["ls-files"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git ls-files failed")
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def run_media_asset_guard(
    repo_root: Path | str,
    product: str,
    material_batch: str,
    output_path: Path | str | None = None,
) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    raw_videos_dir = repo / "products" / product / "inputs" / "raw_videos" / material_batch
    outputs_dir = repo / "products" / product / "outputs"
    raw_exists = raw_videos_dir.exists()
    raw_video_count = 0
    if raw_exists:
        raw_video_count = sum(1 for path in raw_videos_dir.rglob("*") if path.is_file() and path.suffix.lower() in {".mp4", ".mov", ".avi", ".mkv"})

    tracked_media_files = [
        path
        for path in _tracked_files(repo)
        if Path(path).name != ".gitkeep"
        and (Path(path).suffix.lower() in MEDIA_SUFFIXES or "/inputs/raw_videos/" in path)
    ]
    report = {
        "status": "pass" if not tracked_media_files else "fail",
        "raw_videos_dir": str(raw_videos_dir),
        "raw_videos_exists": raw_exists,
        "raw_video_count": raw_video_count,
        "outputs_dir": str(outputs_dir),
        "outputs_git_ignored": _is_git_ignored(repo, outputs_dir),
        "raw_videos_git_ignored": _is_git_ignored(repo, repo / "products" / product / "inputs" / "raw_videos"),
        "tracked_media_files": tracked_media_files,
    }
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
