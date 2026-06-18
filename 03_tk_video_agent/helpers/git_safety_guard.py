"""Git safety checks that prevent media, outputs, and secrets from being staged."""

from __future__ import annotations

import fnmatch
import json
import subprocess
from pathlib import Path
from typing import Any


PROHIBITED_PATTERNS = (
    "products/**/outputs/**",
    "products/**/inputs/raw_videos/**",
    "*.mp4",
    "*.mov",
    "*.avi",
    "*.mkv",
    "*.jpg",
    "*.jpeg",
    "*.png",
    "*.webp",
    "*.wav",
    "*.mp3",
    "*.xlsx",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
)


def _git(repo_root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", *args], cwd=repo_root, capture_output=True, text=True, check=False)


def list_staged_files(repo_root: Path | str) -> list[str]:
    result = _git(Path(repo_root), ["diff", "--cached", "--name-only", "--diff-filter=ACMR"])
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "git diff --cached failed")
    return [line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()]


def is_prohibited_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    name = normalized.rsplit("/", 1)[-1]
    for pattern in PROHIBITED_PATTERNS:
        if fnmatch.fnmatch(normalized, pattern) or fnmatch.fnmatch(name, pattern):
            return True
    return False


def run_git_safety_guard(repo_root: Path | str, output_path: Path | str | None = None) -> dict[str, Any]:
    repo = Path(repo_root).resolve()
    staged_files = list_staged_files(repo)
    prohibited = [path for path in staged_files if is_prohibited_path(path)]
    report = {
        "status": "pass" if not prohibited else "fail",
        "staged_files": staged_files,
        "prohibited_staged_files": prohibited,
        "prohibited_patterns": list(PROHIBITED_PATTERNS),
    }
    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return report
