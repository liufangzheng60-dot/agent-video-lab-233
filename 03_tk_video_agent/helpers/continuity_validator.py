"""Continuity and strict AV sync validation for P12R renders."""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence


DOG_ACTIONS = {"climbing", "descending", "jumping", "paw_placement", "hesitation", "dog_use", "dog_climb"}
PRODUCT_ACTIONS = {"fold", "unfold", "open", "close", "transform", "lock", "release"}


@dataclass(frozen=True)
class ContinuityResult:
    hard_blocks: list[str]
    soft_penalties: list[str]
    av_sync_metrics: dict[str, int | float | bool]
    aesthetic_score: float

    @property
    def passed(self) -> bool:
        return not self.hard_blocks

    def to_dict(self) -> dict[str, Any]:
        return {
            "passed": self.passed,
            "hard_blocks": self.hard_blocks,
            "soft_penalties": self.soft_penalties,
            "av_sync_metrics": self.av_sync_metrics,
            "aesthetic_score": self.aesthetic_score,
        }


def validate_slate_pre_render(
    slate: dict[str, Any],
    alignment: dict[str, Any],
    source_durations_ms: dict[str, int],
) -> ContinuityResult:
    hard: list[str] = []
    soft: list[str] = []
    shots = slate["shots"]
    total_video_ms = sum(int(shot["duration_ms"]) for shot in shots)
    audio_ms = int(alignment["duration_ms"])
    av_error_ms = abs(total_video_ms - audio_ms)
    if av_error_ms > 100:
        hard.append(f"pre-render AV duration mismatch {av_error_ms}ms")
    if int(alignment.get("tail_silence_ms", 0)) > 400:
        hard.append(f"tail silence exceeds 400ms: {alignment['tail_silence_ms']}ms")
    if int(alignment.get("max_internal_silence_ms", 0)) > 700:
        hard.append(f"internal undesigned silence exceeds 700ms: {alignment['max_internal_silence_ms']}ms")
    for shot in shots:
        source_duration_ms = int(shot.get("source_duration_ms", shot["duration_ms"]))
        end_ms = int(shot["source_start_ms"]) + source_duration_ms
        if end_ms > source_durations_ms.get(str(shot["file"]), 0):
            hard.append(f"source bounds exceeded: {shot['file']} {end_ms}ms")
        if not bool(shot.get("action_complete", True)):
            hard.append(f"action truncation risk: {shot['role']} {shot['file']}")
    for prev, shot in zip(shots, shots[1:]):
        if prev["file"] == shot["file"]:
            prev_start = int(prev["source_start_ms"])
            prev_end = prev_start + int(prev.get("source_duration_ms", prev["duration_ms"]))
            cur_start = int(shot["source_start_ms"])
            cur_end = cur_start + int(shot.get("source_duration_ms", shot["duration_ms"]))
            if cur_start < prev_end and cur_end > prev_start:
                hard.append(f"duplicate/overlap window: {prev['file']} {prev['role']}->{shot['role']}")
        if prev.get("shot_scale") == shot.get("shot_scale") and shot.get("shot_scale") != "unknown":
            soft.append(f"same shot scale soft penalty: {prev['role']}->{shot['role']}")
    _claim_evidence_checks(shots, hard)
    _p12s_visual_hygiene_checks(shots, hard)
    _p12s_action_lifecycle_checks(shots, hard)
    _p12s_speed_checks(shots, hard)
    _p12s_lj_cut_checks(shots, hard)
    _p12s_motion_checks(shots, hard, soft)
    metrics = {
        "planned_video_ms": total_video_ms,
        "audio_ms": audio_ms,
        "av_error_ms": av_error_ms,
        "tail_silence_ms": int(alignment.get("tail_silence_ms", 0)),
        "max_internal_silence_ms": int(alignment.get("max_internal_silence_ms", 0)),
    }
    return ContinuityResult(hard, soft, metrics, _score_aesthetic(shots, hard, soft))


def measure_final_av_sync(
    video_path: Path | str,
    alignment: dict[str, Any],
    *,
    target_width: int = 1080,
    target_height: int = 1920,
) -> ContinuityResult:
    streams = probe_streams(video_path)
    duration_ms = probe_duration_ms(video_path)
    audio_ms = _audio_duration_ms(streams) or duration_ms
    hard: list[str] = []
    soft: list[str] = []
    video_stream = next((stream for stream in streams.get("streams", []) if stream.get("codec_type") == "video"), {})
    if int(video_stream.get("width", 0)) != target_width or int(video_stream.get("height", 0)) != target_height:
        hard.append(f"vertical output mismatch: {video_stream.get('width')}x{video_stream.get('height')}")
    av_error_ms = abs(duration_ms - audio_ms)
    tail_ms = max(0, duration_ms - int(alignment.get("last_word_end_ms", duration_ms)))
    internal_ms = int(alignment.get("max_internal_silence_ms", 0))
    if av_error_ms > 100:
        hard.append(f"final AV duration mismatch {av_error_ms}ms")
    if tail_ms > 400:
        hard.append(f"final tail silence exceeds 400ms: {tail_ms}ms")
    if internal_ms > 700:
        hard.append(f"final internal silence exceeds 700ms: {internal_ms}ms")
    metrics = {
        "final_video_ms": duration_ms,
        "final_audio_ms": audio_ms,
        "av_error_ms": av_error_ms,
        "tail_silence_ms": tail_ms,
        "max_internal_silence_ms": internal_ms,
        "width": int(video_stream.get("width", 0)),
        "height": int(video_stream.get("height", 0)),
        "strict_9_16": int(video_stream.get("width", 0)) * 16 == int(video_stream.get("height", 0)) * 9,
    }
    return ContinuityResult(hard, soft, metrics, 0.0)


def probe_duration_ms(path: Path | str) -> int:
    command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {completed.stderr[-400:]}")
    return int(round(float(completed.stdout.strip()) * 1000))


def probe_streams(path: Path | str) -> dict[str, Any]:
    command = ["ffprobe", "-v", "error", "-show_streams", "-of", "json", str(path)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ffprobe streams failed for {path}: {completed.stderr[-400:]}")
    return json.loads(completed.stdout)


def write_validation_report(path: Path | str, payload: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(output)
    return output


def playback_speed(source_duration_ms: int, target_duration_ms: int) -> float:
    if target_duration_ms <= 0:
        raise ValueError("target_duration_ms must be positive")
    return round(float(source_duration_ms) / float(target_duration_ms), 4)


def setpts_expression(speed: float) -> str:
    if speed <= 0:
        raise ValueError("playback speed must be positive")
    return f"setpts=PTS/{speed:.4f}"


def validate_p12s_candidate(
    slate: dict[str, Any],
    alignment: dict[str, Any],
    source_durations_ms: dict[str, int],
) -> ContinuityResult:
    return validate_slate_pre_render(slate, alignment, source_durations_ms)


def _audio_duration_ms(streams: dict[str, Any]) -> int | None:
    for stream in streams.get("streams", []):
        if stream.get("codec_type") == "audio" and stream.get("duration"):
            return int(round(float(stream["duration"]) * 1000))
    return None


def _claim_evidence_checks(shots: Sequence[dict[str, Any]], hard: list[str]) -> None:
    for shot in shots:
        role = str(shot.get("role", "")).lower()
        why = str(shot.get("why", "")).lower() + " " + str(shot.get("claim_evidence", "")).lower()
        if "anti" in role and "paw" not in why and "surface" not in why:
            hard.append(f"anti-slip claim lacks paw/surface evidence: {shot.get('role')}")
        if "transformation" in role and "structure" not in why and "step" not in why:
            hard.append(f"transformation claim lacks visible state change: {shot.get('role')}")


def _p12s_visual_hygiene_checks(shots: Sequence[dict[str, Any]], hard: list[str]) -> None:
    hook_finished = False
    for shot in shots:
        role = str(shot.get("role", "")).lower()
        hand = bool(shot.get("hand_present", False))
        face = bool(shot.get("human_face_present", False))
        body = bool(shot.get("human_body_present", False))
        if face or body:
            hard.append(f"human face/body hard reject: {shot.get('role')} {shot.get('file')}")
        if "hook" not in role:
            hook_finished = True
        if not hand:
            continue
        hand_duration = int(shot.get("hand_duration_ms", shot.get("duration_ms", 0)) or 0)
        hand_action = str(shot.get("hand_action", "")).lower()
        allowed_context = str(shot.get("allowed_hand_context", "none"))
        if "hook" in role and int(shot.get("visual_start_ms", 0)) == 0 and hand_duration <= 800 and allowed_context == "opening_hook":
            continue
        if role in {"transformation", "demonstration"} and allowed_context == "product_transformation" and hand_duration <= 1500 and hand_action in PRODUCT_ACTIONS:
            continue
        if hook_finished:
            hard.append(f"HARD_REJECT_HAND_AFTER_HOOK: {shot.get('role')} {shot.get('file')}")
        else:
            hard.append(f"hand hard reject: {shot.get('role')} {shot.get('file')}")


def _p12s_action_lifecycle_checks(shots: Sequence[dict[str, Any]], hard: list[str]) -> None:
    strict_roles = ("outcome", "proof", "transformation")
    for shot in shots:
        role = str(shot.get("role", "")).lower()
        if not any(item in role for item in strict_roles):
            continue
        completeness = str(shot.get("action_completeness", "complete")).lower()
        completion = int(shot.get("kinematic_completion_ms", 0) or 0)
        settle = int(shot.get("kinematic_settle_end_ms", 0) or 0)
        duration = int(shot.get("duration_ms", 0) or 0)
        if completeness in {"incomplete", "onset_only", "completion_missing", "result_not_visible", "truncated"}:
            hard.append(f"{shot.get('role')} action incomplete: {completeness}")
        if completion <= 0 or settle <= 0 or settle > duration + 80 or completion > settle:
            hard.append(f"{shot.get('role')} missing completion/settle lifecycle")
        if "transformation" in role:
            state = str(shot.get("product_state_result", "complete")).lower()
            if state in {"mid_state", "half_folded", "half_open", "unknown"}:
                hard.append(f"transformation lacks final state: {shot.get('file')}")


def _p12s_speed_checks(shots: Sequence[dict[str, Any]], hard: list[str]) -> None:
    for shot in shots:
        speed = float(shot.get("playback_speed", 1.0) or 1.0)
        action_type = str(shot.get("action_type", "")).lower()
        subject = str(shot.get("action_subject", "")).lower()
        if action_type in DOG_ACTIONS or subject == "dog":
            if speed > 1.08:
                hard.append(f"HARD_REJECT_UNNATURAL_ANIMAL_SPEED: {shot.get('role')} {speed}")
        if action_type in PRODUCT_ACTIONS or subject == "product":
            if speed > 1.25:
                hard.append(f"product action speed exceeds 1.25x: {shot.get('role')} {speed}")


def _p12s_lj_cut_checks(shots: Sequence[dict[str, Any]], hard: list[str]) -> None:
    for shot in shots:
        l_cut = int(shot.get("l_cut_ms", 0) or 0)
        j_cut = int(shot.get("j_cut_ms", 0) or 0)
        if l_cut and not (150 <= l_cut <= int(shot.get("l_cut_max_ms", 450) or 450)):
            hard.append(f"L-Cut out of range: {shot.get('role')} {l_cut}ms")
        if j_cut and not (120 <= j_cut <= 350):
            hard.append(f"J-Cut out of range: {shot.get('role')} {j_cut}ms")
        if (l_cut or j_cut) and bool(shot.get("semantic_conflict", False)):
            hard.append(f"L/J-Cut semantic conflict: {shot.get('role')}")


def _p12s_motion_checks(shots: Sequence[dict[str, Any]], hard: list[str], soft: list[str]) -> None:
    static_wide_run = 0
    for prev, shot in zip(shots, shots[1:]):
        prev_dir = str(prev.get("subject_motion_direction", "none"))
        cur_dir = str(shot.get("subject_motion_direction", "none"))
        if prev_dir in {"left", "right"} and cur_dir in {"left", "right"} and prev_dir != cur_dir and not shot.get("direction_reversal_justified", False):
            hard.append(f"motion direction reversal: {prev.get('role')}->{shot.get('role')}")
        if prev.get("camera_motion") == "push_in" and shot.get("shot_scale") == "wide":
            soft.append(f"push-in to wide soft penalty: {prev.get('role')}->{shot.get('role')}")
    for shot in shots:
        if str(shot.get("camera_motion", "static")) == "static" and "wide" in str(shot.get("shot_scale", "")).lower():
            static_wide_run += 1
            if static_wide_run >= 3:
                soft.append("three static wide shots in a row")
        else:
            static_wide_run = 0


def _score_aesthetic(shots: Sequence[dict[str, Any]], hard: Sequence[str], soft: Sequence[str]) -> float:
    score = 82.0 - len(hard) * 20.0 - len(soft) * 1.5
    files = [str(shot.get("file")) for shot in shots]
    if len(set(files)) >= min(4, len(files)):
        score += 4
    if shots and int(shots[0].get("duration_ms", 0)) <= 2800:
        score += 3
    if any("dog" in str(shot.get("why", "")).lower() for shot in shots):
        score += 3
    return round(max(0.0, min(100.0, score)), 2)
