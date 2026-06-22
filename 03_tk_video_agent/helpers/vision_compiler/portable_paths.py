"""Portable repository and data-root path helpers for Windows desktops."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path


def repo_root(start: Path | None = None) -> Path:
    """Resolve the Git repository root without relying on a machine path."""
    current = (start or Path(__file__)).resolve()
    if current.is_file():
        current = current.parent
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=current,
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode == 0 and completed.stdout.strip():
            return Path(completed.stdout.strip()).resolve()
    except Exception:
        pass
    for candidate in [current, *current.parents]:
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError(f"Cannot resolve Git repository root from {current}")


def data_root(*, create: bool = False) -> Path:
    """Return the media/data root.

    `AGENT_VIDEO_DATA_ROOT` is authoritative. When unset, use a
    repository-external local test data directory so a clean Git clone remains
    small and generated smoke-test media does not enter the working tree.
    """
    env_value = os.environ.get("AGENT_VIDEO_DATA_ROOT")
    if env_value:
        root = Path(env_value).expanduser().resolve()
    else:
        repo = repo_root()
        root = repo.parent / "agent_video_data_local"
    if create:
        root.mkdir(parents=True, exist_ok=True)
    return root


def data_path(*parts: str, create_parent: bool = False) -> Path:
    path = data_root(create=create_parent).joinpath(*parts)
    if create_parent:
        path.parent.mkdir(parents=True, exist_ok=True)
    return path


def agent_root() -> Path:
    return repo_root() / "03_tk_video_agent"


def config_path(*parts: str) -> Path:
    return agent_root().joinpath("configs", *parts)
