"""Frame-level transition freeze detector for P12T.

VLM can judge story quality, but this module owns physical freeze detection.
It compares final-output frames around each cut with the corresponding source
window so natural source stillness is not mistaken for renderer failure.
"""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import numpy as np
from PIL import Image


FPS = 30
FRAME_MS = 1000.0 / FPS


@dataclass(frozen=True)
class FrameStats:
    frame_count: int
    exact_duplicate_tail_frames: int
    exact_duplicate_tail_ms: float
    near_static_tail_frames: int
    near_static_tail_ms: float
    mean_abs_diff: float
    motion_energy: float


def quantize_duration_ms(duration_ms: int | float, fps: int = FPS) -> dict[str, Any]:
    target_frames = max(1, int(round(float(duration_ms) * fps / 1000.0)))
    quantized_ms = target_frames * 1000.0 / fps
    return {
        "requested_duration_ms": float(duration_ms),
        "target_frames": target_frames,
        "quantized_duration_ms": quantized_ms,
        "duration_quantization_error_ms": quantized_ms - float(duration_ms),
    }


def build_transition_points(slate: dict[str, Any]) -> list[dict[str, Any]]:
    shots = slate["shots"]
    transitions: list[dict[str, Any]] = []
    for index, (prev, nxt) in enumerate(zip(shots, shots[1:]), start=1):
        transitions.append(
            {
                "transition_index": index,
                "cut_time_ms": int(prev["visual_end_ms"]),
                "previous_clip_id": f"{prev['role']}:{prev['file']}",
                "next_clip_id": f"{nxt['role']}:{nxt['file']}",
                "previous_shot": prev,
                "next_shot": nxt,
            }
        )
    return transitions


def analyze_video_transitions(
    video_path: Path | str,
    slate: dict[str, Any],
    raw_dir: Path | str,
    *,
    output_fps: int = FPS,
    pre_ms: int = 500,
    post_ms: int = 200,
    dynamic_freeze_threshold_ms: int = 100,
    near_static_diff_threshold: float = 1.5,
    source_motion_threshold: float = 2.5,
) -> dict[str, Any]:
    video = Path(video_path)
    raw_root = Path(raw_dir)
    transitions = []
    for transition in build_transition_points(slate):
        cut_ms = int(transition["cut_time_ms"])
        prev = transition["previous_shot"]
        output_frames = extract_frames(video, max(0, cut_ms - pre_ms), pre_ms + post_ms, fps=output_fps)
        source_end_ms = int(prev["source_start_ms"]) + int(prev.get("source_duration_ms", prev["duration_ms"]))
        source_frames = extract_frames(raw_root / str(prev["file"]), max(0, source_end_ms - pre_ms), pre_ms, fps=output_fps)
        try:
            output_pre_frames = output_frames[: max(1, int(round(pre_ms * output_fps / 1000.0)))]
            output_stats = compute_frame_stats(output_pre_frames, near_static_diff_threshold=near_static_diff_threshold)
            source_stats = compute_frame_stats(source_frames, near_static_diff_threshold=near_static_diff_threshold)
        finally:
            _cleanup_frame_paths(output_frames)
            _cleanup_frame_paths(source_frames)
        intentional_hold = bool(prev.get("intentional_hold", False))
        editorial_role = str(prev.get("editorial_role", prev.get("role", ""))).lower()
        source_static = source_stats.motion_energy <= source_motion_threshold
        output_freeze_ms = max(output_stats.exact_duplicate_tail_ms, output_stats.near_static_tail_ms)
        pipeline_introduced = (
            not intentional_hold
            and output_freeze_ms > dynamic_freeze_threshold_ms
            and not source_static
            and output_stats.motion_energy <= max(0.1, source_stats.motion_energy * 0.1)
        )
        if pipeline_introduced:
            root_cause = "PIPELINE_INTRODUCED_FREEZE"
            result = "hard_reject"
        elif source_static:
            root_cause = "SOURCE_NATURAL_STATIC"
            result = "pass_rhythm_review_required"
        elif intentional_hold and editorial_role in {"hero", "detail", "closure"}:
            root_cause = "INTENTIONAL_HOLD"
            result = "pass"
        else:
            root_cause = "NO_FREEZE_DETECTED" if output_freeze_ms <= dynamic_freeze_threshold_ms else "MOTION_ENERGY_RISK"
            result = "pass" if root_cause == "NO_FREEZE_DETECTED" else "review"
        transitions.append(
            {
                "transition_index": transition["transition_index"],
                "cut_time_ms": cut_ms,
                "previous_clip_id": transition["previous_clip_id"],
                "next_clip_id": transition["next_clip_id"],
                "exact_duplicate_run_frames": output_stats.exact_duplicate_tail_frames,
                "exact_duplicate_run_ms": round(output_stats.exact_duplicate_tail_ms, 2),
                "near_static_run_ms": round(output_stats.near_static_tail_ms, 2),
                "mean_abs_diff": round(output_stats.mean_abs_diff, 4),
                "source_motion_energy": round(source_stats.motion_energy, 4),
                "output_motion_energy": round(output_stats.motion_energy, 4),
                "pipeline_introduced_freeze": pipeline_introduced,
                "intentional_hold": intentional_hold,
                "root_cause": root_cause,
                "transition_result": result,
                "repair_action": "required" if pipeline_introduced else "none",
            }
        )
    hard_rejects = [item for item in transitions if item["pipeline_introduced_freeze"]]
    return {
        "video_path": str(video),
        "fps": output_fps,
        "transition_count": len(transitions),
        "hard_reject_count": len(hard_rejects),
        "max_freeze_ms": max((max(item["exact_duplicate_run_ms"], item["near_static_run_ms"]) for item in transitions), default=0),
        "transitions": transitions,
        "passed": not hard_rejects,
    }


def compute_frame_stats(frames: Sequence[Path], *, near_static_diff_threshold: float = 1.5) -> FrameStats:
    if not frames:
        return FrameStats(0, 0, 0.0, 0, 0.0, 0.0, 0.0)
    hashes = [_hash_file(path) for path in frames]
    arrays = [_load_gray(path) for path in frames]
    diffs = [float(np.mean(np.abs(arrays[index].astype(np.int16) - arrays[index - 1].astype(np.int16)))) for index in range(1, len(arrays))]
    exact_tail = 1
    for index in range(len(hashes) - 1, 0, -1):
        if hashes[index] == hashes[index - 1]:
            exact_tail += 1
        else:
            break
    near_tail = 1
    for value in reversed(diffs):
        if value <= near_static_diff_threshold:
            near_tail += 1
        else:
            break
    return FrameStats(
        frame_count=len(frames),
        exact_duplicate_tail_frames=exact_tail if exact_tail > 1 else 0,
        exact_duplicate_tail_ms=(exact_tail - 1) * FRAME_MS if exact_tail > 1 else 0.0,
        near_static_tail_frames=near_tail if near_tail > 1 else 0,
        near_static_tail_ms=(near_tail - 1) * FRAME_MS if near_tail > 1 else 0.0,
        mean_abs_diff=float(np.mean(diffs)) if diffs else 0.0,
        motion_energy=float(np.mean(diffs)) if diffs else 0.0,
    )


def extract_frames(video_path: Path | str, start_ms: int, duration_ms: int, *, fps: int = FPS) -> list[Path]:
    tmp = Path(tempfile.mkdtemp(prefix="transition_frames_"))
    output_pattern = tmp / "frame_%04d.png"
    command = [
        "ffmpeg",
        "-hide_banner",
        "-loglevel",
        "error",
        "-ss",
        f"{start_ms / 1000.0:.3f}",
        "-i",
        str(video_path),
        "-t",
        f"{duration_ms / 1000.0:.3f}",
        "-vf",
        f"fps={fps},scale=180:-1",
        str(output_pattern),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        raise RuntimeError(f"frame extraction failed: {completed.stderr[-500:]}")
    frames = sorted(tmp.glob("frame_*.png"))
    return frames


def probe_frame_count(path: Path | str) -> int:
    command = [
        "ffprobe",
        "-v",
        "error",
        "-select_streams",
        "v:0",
        "-count_frames",
        "-show_entries",
        "stream=nb_read_frames",
        "-of",
        "default=nk=1:nw=1",
        str(path),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ffprobe frame count failed: {completed.stderr[-400:]}")
    return int((completed.stdout.strip() or "0").splitlines()[0])


def cleanup_extracted_frames(report: dict[str, Any]) -> None:
    # extract_frames intentionally returns paths for direct use; caller can remove
    # temp dirs by deleting the parent of any frame path it keeps.
    return None


def _cleanup_frame_paths(frames: Sequence[Path]) -> None:
    parents = {path.parent for path in frames}
    for parent in parents:
        shutil.rmtree(parent, ignore_errors=True)


def write_json(path: Path | str, payload: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(output)
    return output


def _hash_file(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


def _load_gray(path: Path) -> np.ndarray:
    return np.asarray(Image.open(path).convert("L"), dtype=np.uint8)
