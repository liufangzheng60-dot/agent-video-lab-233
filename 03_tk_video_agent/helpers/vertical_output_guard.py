"""TikTok 9:16 hard output guard.

The guard is deterministic for container and segment geometry. Semantic crop
quality is marked pending for VLM/Owner review; VLM may not override failures.
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FINAL_WIDTH = 1080
FINAL_HEIGHT = 1920
ALLOWED_QC_DRAFT_SIZES = {(360, 640), (540, 960), (720, 1280)}
MAX_REPLACEMENT_ATTEMPTS = 3
MIN_FRAME_FILL_RATIO = 0.97


@dataclass
class VerticalOutputGuard:
    """Validate final and segment-level true 9:16 output readiness."""

    min_frame_fill_ratio: float = MIN_FRAME_FILL_RATIO

    def probe_video(self, path: Path | str) -> dict[str, Any]:
        video_path = Path(path)
        if video_path.suffix.lower() == ".json":
            return json.loads(video_path.read_text(encoding="utf-8-sig")).get("final_container", {})
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-select_streams",
                "v:0",
                "-show_entries",
                "stream=width,height,display_aspect_ratio,sample_aspect_ratio",
                "-of",
                "json",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            return {"probe_error": result.stderr.strip() or "ffprobe_failed"}
        payload = json.loads(result.stdout)
        streams = payload.get("streams", [])
        if not streams:
            return {"probe_error": "no_video_stream"}
        stream = streams[0]
        width = int(stream.get("width", 0))
        height = int(stream.get("height", 0))
        return {
            "width": width,
            "height": height,
            "display_aspect_ratio": stream.get("display_aspect_ratio") or _ratio_text(width, height),
            "sample_aspect_ratio": stream.get("sample_aspect_ratio") or "1:1",
            "orientation": "portrait" if height > width else "landscape",
        }

    def validate_final_container(self, path_or_metadata: Path | str | dict[str, Any], *, qc_draft: bool = False) -> dict[str, Any]:
        metadata = path_or_metadata if isinstance(path_or_metadata, dict) else self.probe_video(path_or_metadata)
        width = int(metadata.get("width", 0))
        height = int(metadata.get("height", 0))
        expected_size = (width, height) in ALLOWED_QC_DRAFT_SIZES if qc_draft else (width, height) == (FINAL_WIDTH, FINAL_HEIGHT)
        failures = []
        if not expected_size:
            failures.append("invalid_container_size")
        if metadata.get("display_aspect_ratio", _ratio_text(width, height)) not in {"9:16", "0.5625"}:
            failures.append("invalid_display_aspect_ratio")
        if metadata.get("sample_aspect_ratio", "1:1") not in {"1:1", "0:1"}:
            failures.append("invalid_sample_aspect_ratio")
        if metadata.get("orientation", "portrait") != "portrait":
            failures.append("invalid_orientation")
        return {"pass": not failures, "failures": failures, "metadata": metadata}

    def validate_segment_plan(self, segment: dict[str, Any]) -> dict[str, Any]:
        segment_id = segment.get("segment_id") or segment.get("id") or "unknown_segment"
        failures = []
        warnings = []
        output_width = int(segment.get("output_width", 0))
        output_height = int(segment.get("output_height", 0))
        if _ratio_text(output_width, output_height) != "9:16":
            failures.append("segment_output_not_9x16")
        if segment.get("black_bar_detected"):
            failures.append("black_bar_detected")
        if segment.get("letterbox_detected"):
            failures.append("letterbox_detected")
        if segment.get("pillarbox_detected"):
            failures.append("pillarbox_detected")
        if segment.get("stretch_detected") or self.detect_stretch(segment):
            failures.append("stretch_detected")
        if float(segment.get("frame_fill_ratio", 1.0)) < self.min_frame_fill_ratio:
            failures.append("frame_fill_too_low")
        if segment.get("fit_policy") in {"inset", "letterbox", "pillarbox", "blur_background"}:
            failures.append("forbidden_fit_policy")
        crop_result = _validate_crop_box(segment)
        failures.extend(crop_result["failures"])
        if segment.get("semantic_crop_risk") or segment.get("subject_safe_zone") == "unsafe":
            warnings.append("semantic_crop_pending")
        result = "pass" if not failures else "fail"
        if warnings and result == "pass":
            result = "hold"
        return {
            "segment_id": segment_id,
            "segment_gate_result": result,
            "failures": failures,
            "warnings": warnings,
            "replacement_required": bool(failures),
            "time_range": segment.get("time_range") or [segment.get("start_sec"), segment.get("end_sec")],
        }

    def sample_segment_boundary_frames(self, video_path: Path | str, timeline: dict[str, Any]) -> list[dict[str, Any]]:
        samples = []
        for segment in timeline.get("segments", []):
            start = float(segment.get("start_sec", 0))
            end = float(segment.get("end_sec", start))
            midpoint = start + max(0, end - start) / 2
            for label, timestamp in (("start_plus_0_1", start + 0.1), ("midpoint", midpoint), ("end_minus_0_1", max(start, end - 0.1))):
                samples.append({"segment_id": segment.get("segment_id", "unknown_segment"), "label": label, "timestamp": round(timestamp, 3), "video_path": str(video_path)})
            samples.append({"segment_id": segment.get("segment_id", "unknown_segment"), "label": "transition_before", "timestamp": round(max(start, end - 0.02), 3), "video_path": str(video_path)})
            samples.append({"segment_id": segment.get("segment_id", "unknown_segment"), "label": "transition_after", "timestamp": round(end + 0.02, 3), "video_path": str(video_path)})
        return samples

    def detect_black_bars(self, frame_path: Path | str) -> bool:
        metadata = _load_frame_metadata(frame_path)
        return bool(metadata.get("black_bar_detected") or metadata.get("letterbox_detected") or metadata.get("pillarbox_detected"))

    def detect_stretch(self, metadata: dict[str, Any]) -> bool:
        if metadata.get("stretch_detected"):
            return True
        source_ratio = _ratio_value(int(metadata.get("source_width", 0)), int(metadata.get("source_height", 0)))
        output_ratio = _ratio_value(int(metadata.get("output_width", 0)), int(metadata.get("output_height", 0)))
        fit_policy = metadata.get("fit_policy")
        if fit_policy in {"stretch", "force_fill"}:
            return True
        return bool(metadata.get("non_uniform_scale")) or (fit_policy == "scale" and source_ratio and output_ratio and abs(source_ratio - output_ratio) > 0.05)

    def calculate_frame_fill(self, frame_path: Path | str) -> float:
        metadata = _load_frame_metadata(frame_path)
        return float(metadata.get("frame_fill_ratio", 1.0))

    def build_vertical_compliance_report(self, manifest_or_video: Path | str | dict[str, Any], *, variant_id: str | None = None, qc_draft: bool = False) -> dict[str, Any]:
        payload = _load_manifest(manifest_or_video)
        final_metadata = payload.get("final_container") if isinstance(payload, dict) else None
        final_result = self.validate_final_container(final_metadata or manifest_or_video, qc_draft=qc_draft)
        segments = payload.get("segments", []) if isinstance(payload, dict) else []
        segment_results = [self.validate_segment_plan(segment) for segment in segments]
        failed = [item for item in segment_results if item["segment_gate_result"] == "fail"]
        semantic_pending = [item["segment_id"] for item in segment_results if "semantic_crop_pending" in item["warnings"]]
        report = {
            "variant_id": variant_id or (payload.get("variant_id") if isinstance(payload, dict) else Path(str(manifest_or_video)).stem),
            "final_container_pass": final_result["pass"],
            "segment_count": len(segments),
            "segments_passed": sum(1 for item in segment_results if item["segment_gate_result"] == "pass"),
            "segments_failed": len(failed),
            "failed_segment_ids": [item["segment_id"] for item in failed],
            "failed_time_ranges": {item["segment_id"]: item["time_range"] for item in failed},
            "black_bar_failures": _failure_ids(failed, "black_bar"),
            "stretch_failures": _failure_ids(failed, "stretch"),
            "frame_fill_failures": _failure_ids(failed, "frame_fill"),
            "semantic_crop_pending": semantic_pending,
            "auto_replacement_required": bool(failed),
            "publish_allowed": final_result["pass"] and not failed and not semantic_pending,
            "release_allowed": final_result["pass"] and not failed and not semantic_pending,
            "risk_flags": list(final_result["failures"]),
            "segment_results": segment_results,
        }
        if failed:
            report["risk_flags"].append("segment_level_9x16_failure")
        if semantic_pending:
            report["risk_flags"].append("semantic_crop_pending")
        return report

    def recommend_replacement(self, failed_segment: dict[str, Any]) -> dict[str, Any]:
        attempts = int(failed_segment.get("replacement_attempts", 0))
        if attempts >= MAX_REPLACEMENT_ATTEMPTS:
            return {"action": "hold_variant", "reason": "max_replacement_attempts_reached", "attempts": attempts}
        return {
            "action": "replace_segment",
            "attempt": attempts + 1,
            "allowed_order": [
                "safe_smart_crop_window",
                "adjust_crop_anchor",
                "alternate_time_window_same_asset",
                "alternate_strategy_compatible_asset",
                "variant_hold_or_reject",
            ],
            "forbidden": ["stretch", "horizontal_inset", "black_bar_fill", "unapproved_blur_background"],
        }

    def validate_publish_readiness(self, report: dict[str, Any]) -> dict[str, Any]:
        allowed = bool(report.get("publish_allowed") and report.get("release_allowed"))
        return {"publish_allowed": allowed, "release_allowed": allowed, "status": "pass" if allowed else "fail", "risk_flags": report.get("risk_flags", [])}


def build_shortage_report(target_count: int, passed_count: int, held_variants: list[str]) -> dict[str, Any]:
    return {
        "target_count": target_count,
        "passed_count": passed_count,
        "shortage_count": max(0, target_count - passed_count),
        "held_variants": held_variants,
        "status": "shortage" if passed_count < target_count else "filled",
    }


def _load_manifest(value: Path | str | dict[str, Any]) -> dict[str, Any]:
    if isinstance(value, dict):
        return value
    path = Path(value)
    if path.suffix.lower() == ".json":
        return json.loads(path.read_text(encoding="utf-8-sig"))
    return {}


def _load_frame_metadata(path: Path | str) -> dict[str, Any]:
    frame_path = Path(path)
    if frame_path.suffix.lower() == ".json" and frame_path.exists():
        return json.loads(frame_path.read_text(encoding="utf-8-sig"))
    return {}


def _ratio_value(width: int, height: int) -> float | None:
    if not width or not height:
        return None
    return width / height


def _ratio_text(width: int, height: int) -> str:
    if not width or not height:
        return "unknown"
    if abs((width / height) - (9 / 16)) < 0.002:
        return "9:16"
    return f"{width}:{height}"


def _validate_crop_box(segment: dict[str, Any]) -> dict[str, list[str]]:
    crop = segment.get("crop_box")
    if not crop:
        return {"failures": ["missing_crop_box"]}
    source_width = int(segment.get("source_width", 0))
    source_height = int(segment.get("source_height", 0))
    x = int(crop.get("x", 0))
    y = int(crop.get("y", 0))
    width = int(crop.get("width", 0))
    height = int(crop.get("height", 0))
    failures = []
    if width <= 0 or height <= 0:
        failures.append("invalid_crop_box")
    if source_width and source_height and (x < 0 or y < 0 or x + width > source_width or y + height > source_height):
        failures.append("crop_box_out_of_bounds")
    if _ratio_text(width, height) != "9:16":
        failures.append("crop_box_not_9x16")
    return {"failures": failures}


def _failure_ids(failed_results: list[dict[str, Any]], needle: str) -> list[str]:
    return [item["segment_id"] for item in failed_results if any(needle in failure for failure in item["failures"])]
