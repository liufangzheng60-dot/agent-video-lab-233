from __future__ import annotations

import json
import subprocess
from pathlib import Path


ACTIVE_EXTS = {".py", ".ps1", ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg"}
EXCLUDE_DIRS = {".git", ".venv", "venv", "__pycache__", ".pytest_cache", "products", "outputs", "inputs", "docs"}


def repo_root() -> Path:
    completed = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
    if completed.returncode == 0 and completed.stdout.strip():
        return Path(completed.stdout.strip()).resolve()
    return Path(__file__).resolve().parents[1]


def iter_active_files(root: Path):
    roots = [root / "03_tk_video_agent" / "helpers", root / "03_tk_video_agent" / "configs", root / "03_tk_video_agent" / "tests", root / "scripts"]
    for base in roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in ACTIVE_EXTS:
                continue
            if any(part in EXCLUDE_DIRS for part in path.relative_to(root).parts):
                continue
            yield path


def git_ignored(root: Path, rel: str) -> bool:
    completed = subprocess.run(["git", "check-ignore", "-q", rel], cwd=root, check=False)
    return completed.returncode == 0


def main() -> int:
    root = repo_root()
    user_path = "C:" + "\\Users" + "\\43871"
    repo_name = "agent-video-lab-233-" + "laptop"
    findings = []
    for path in iter_active_files(root):
        text = path.read_text(encoding="utf-8", errors="ignore")
        for pattern in [user_path, repo_name]:
            if pattern in text:
                findings.append({"file": str(path.relative_to(root)), "pattern": pattern})

    config_findings = []
    for path in (root / "03_tk_video_agent" / "configs").glob("*"):
        if not path.is_file() or path.suffix.lower() not in {".json", ".yaml", ".yml"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if "C:\\" in text or "\\Users\\" in text:
            config_findings.append(str(path.relative_to(root)))

    ignore_targets = [".env", ".env.local", ".venv/pyvenv.cfg", "products/dog_stairs_v1/outputs/x.mp4", "products/dog_stairs_v1/inputs/raw_videos/x.mov"]
    ignore_report = {target: git_ignored(root, target) for target in ignore_targets}
    report = {
        "repo_root": str(root),
        "hardcoded_path_findings": findings,
        "config_absolute_path_findings": config_findings,
        "git_ignore_report": ignore_report,
        "overall_pass": not findings and not config_findings and all(ignore_report.values()),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
