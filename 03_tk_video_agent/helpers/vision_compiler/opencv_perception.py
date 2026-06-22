"""OpenCV-backed pixel and micro-timing perception for P12W."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import cv2
import numpy as np


FPS = 30
VIDEO_EXTENSIONS = {".mov", ".mp4", ".m4v"}


@dataclass(frozen=True)
class CvEnvironment:
    python_executable: str
    python_version: str
    pip_version: str
    numpy_version: str
    skimage_version: str | None
    opencv_version: str
    opencv_backend_used: bool


def inspect_environment() -> dict[str, Any]:
    import pip
    import sys

    try:
        import skimage

        skimage_version = skimage.__version__
    except Exception:
        skimage_version = None
    return {
        "python_executable": sys.executable,
        "python_version": sys.version,
        "pip_version": pip.__version__,
        "numpy_version": np.__version__,
        "skimage_version": skimage_version,
        "opencv_version": cv2.__version__,
        "opencv_backend_used": True,
    }


def validate_opencv_video_path(video_path: Path | str) -> dict[str, Any]:
    path = Path(video_path)
    cap = cv2.VideoCapture(str(path))
    ok1, frame1 = cap.read()
    ok2, frame2 = cap.read()
    cap.release()
    if not ok1 or not ok2:
        raise RuntimeError(f"OpenCV failed to decode two frames from {path}")
    g1 = _gray_resize(frame1)
    g2 = _gray_resize(frame2)
    flow = cv2.calcOpticalFlowFarneback(g1, g2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    pts = cv2.goodFeaturesToTrack(g1, maxCorners=120, qualityLevel=0.01, minDistance=7)
    if pts is None or len(pts) < 8:
        raise RuntimeError("OpenCV feature detector did not find enough points")
    nxt, status, _ = cv2.calcOpticalFlowPyrLK(g1, g2, pts, None)
    good_old = pts[status.flatten() == 1]
    good_new = nxt[status.flatten() == 1]
    mat, inliers = cv2.estimateAffinePartial2D(good_old, good_new, method=cv2.RANSAC)
    if mat is None:
        raise RuntimeError("OpenCV affine RANSAC failed")
    return {
        "video_read": True,
        "farneback": True,
        "features": int(len(pts)),
        "affine_ransac": True,
        "laplacian": float(cv2.Laplacian(g1, cv2.CV_64F).var()),
        "histogram": float(cv2.calcHist([g1], [0], None, [256], [0, 256]).sum()),
        "frame_diff": float(np.mean(np.abs(g2.astype(np.int16) - g1.astype(np.int16)))),
        "flow_shape": list(flow.shape),
        "inlier_ratio": float(np.mean(inliers)) if inliers is not None else 0.0,
    }


def build_asset_perception_index(raw_dir: Path | str, output_dir: Path | str, *, sample_fps: float = 2.0) -> dict[str, Any]:
    raw = Path(raw_dir)
    out = Path(output_dir)
    assets = []
    for path in sorted(item for item in raw.iterdir() if item.suffix.lower() in VIDEO_EXTENSIONS):
        assets.append(analyze_video_file(path, sample_fps=sample_fps))
    payload = {
        "spec_version": "P12W-v1",
        "opencv_backend_used": True,
        "opencv_version": cv2.__version__,
        "asset_count": len(assets),
        "coverage": f"{len(assets)}/{len(list(raw.glob('*.*')))}",
        "assets": assets,
    }
    write_json(out / "opencv_asset_perception_index.json", payload)
    write_json(out / "motion_descriptor_index.json", {
        "spec_version": "P12W-v1",
        "opencv_backend_used": True,
        "descriptors": {asset["source_video_id"]: asset["motion_descriptors"] for asset in assets},
    })
    return payload


def analyze_video_file(path: Path | str, *, sample_fps: float = 2.0) -> dict[str, Any]:
    video = Path(path)
    probe = ffprobe_json(video)
    stream = next(item for item in probe["streams"] if item.get("codec_type") == "video")
    duration_ms = int(round(float(probe["format"]["duration"]) * 1000))
    fps = _rate_to_float(stream.get("avg_frame_rate") or stream.get("r_frame_rate") or "30/1")
    cap = cv2.VideoCapture(str(video))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    step = max(1, int(round(fps / sample_fps)))
    frames: list[np.ndarray] = []
    times: list[int] = []
    index = 0
    while True:
        ok, frame = cap.read()
        if not ok:
            break
        if index % step == 0:
            frames.append(_gray_resize(frame))
            times.append(int(round(index * 1000.0 / max(fps, 1e-6))))
        index += 1
    cap.release()
    metrics = compute_sequence_metrics(frames, times)
    return {
        "source_video_id": video.stem,
        "source_path": str(video),
        "file_hash": file_hash(video),
        "width": int(stream.get("width", 0)),
        "height": int(stream.get("height", 0)),
        "fps": fps,
        "duration_ms": duration_ms,
        "codec": stream.get("codec_name"),
        "frame_count": frame_count,
        "rotation": stream.get("tags", {}).get("rotate", "0"),
        "frame_interval_stats": {"sample_step": step, "sample_count": len(frames), "nominal_fps": fps},
        **metrics,
    }


def compute_sequence_metrics(frames: list[np.ndarray], times: list[int]) -> dict[str, Any]:
    if not frames:
        return _empty_metrics()
    blur = [float(cv2.Laplacian(frame, cv2.CV_64F).var()) for frame in frames]
    tenengrad = [_tenengrad(frame) for frame in frames]
    exposure = [_exposure(frame) for frame in frames]
    diffs = [float(np.mean(np.abs(frames[i].astype(np.int16) - frames[i - 1].astype(np.int16)))) for i in range(1, len(frames))]
    duplicate_ranges = _duplicate_ranges(frames, times)
    freeze_ranges = _near_static_ranges(diffs, times)
    abab_ranges = detect_abab_ranges(frames, times)
    motion_curve = [{"time_ms": times[i], "motion_energy": round(diffs[i - 1], 4)} for i in range(1, len(frames))]
    global_curve = []
    local_curve = []
    shake_curve = []
    for i in range(1, len(frames)):
        motion = estimate_motion_pair(frames[i - 1], frames[i])
        global_curve.append({"time_ms": times[i], **motion["global_motion"]})
        local_curve.append({"time_ms": times[i], **motion["local_motion"]})
        shake_curve.append({"time_ms": times[i], "shake_score": motion["shake_score"]})
    glitch_ranges = _glitch_ranges(diffs, times, abab_ranges, duplicate_ranges)
    quality = _technical_quality(blur, exposure, diffs, duplicate_ranges, glitch_ranges)
    return {
        "blur_curve": _curve(times, blur, "laplacian_var"),
        "tenengrad_curve": _curve(times, tenengrad, "tenengrad"),
        "exposure_curve": exposure,
        "highlight_clip_ratio": round(float(np.median([item["highlight_clip_ratio"] for item in exposure])), 6),
        "shadow_clip_ratio": round(float(np.median([item["shadow_clip_ratio"] for item in exposure])), 6),
        "motion_energy_curve": motion_curve,
        "global_motion_curve": global_curve,
        "local_motion_curve": local_curve,
        "shake_curve": shake_curve,
        "duplicate_frame_ranges": duplicate_ranges,
        "freeze_ranges": freeze_ranges,
        "abab_frame_ranges": abab_ranges,
        "glitch_risk_ranges": glitch_ranges,
        "motion_peak_ranges": sorted(motion_curve, key=lambda item: item["motion_energy"], reverse=True)[:5],
        "technical_quality_score": quality["technical_quality_score"],
        "safe_crop_score": 100.0,
        "motion_descriptors": {
            "head": window_motion_descriptor(frames[: max(2, min(len(frames), 3))]),
            "tail": window_motion_descriptor(frames[max(0, len(frames) - 3) :]),
        },
        "artifact_summary": quality,
    }


def estimate_motion_pair(first: np.ndarray, second: np.ndarray) -> dict[str, Any]:
    pts = cv2.goodFeaturesToTrack(first, maxCorners=160, qualityLevel=0.01, minDistance=7)
    global_motion = _zero_global("uncertain")
    if pts is not None and len(pts) >= 8:
        nxt, status, _ = cv2.calcOpticalFlowPyrLK(first, second, pts, None)
        good_old = pts[status.flatten() == 1]
        good_new = nxt[status.flatten() == 1]
        if len(good_old) >= 8:
            mat, inliers = cv2.estimateAffinePartial2D(good_old, good_new, method=cv2.RANSAC, ransacReprojThreshold=3)
            if mat is not None:
                dx = float(mat[0, 2])
                dy = float(mat[1, 2])
                mag = math.hypot(dx, dy)
                global_motion = {
                    "dx": round(dx, 4),
                    "dy": round(dy, 4),
                    "magnitude": round(mag, 4),
                    "angle_deg": round(math.degrees(math.atan2(dy, dx)) if mag else 0.0, 4),
                    "rotation_deg": round(math.degrees(math.atan2(float(mat[1, 0]), float(mat[0, 0]))), 4),
                    "scale": round(float((mat[0, 0] ** 2 + mat[1, 0] ** 2) ** 0.5), 5),
                    "inlier_ratio": round(float(np.mean(inliers)) if inliers is not None else 0.0, 4),
                    "confidence": round(float(np.mean(inliers)) if inliers is not None else 0.0, 4),
                }
    flow = cv2.calcOpticalFlowFarneback(first, second, None, 0.5, 3, 15, 3, 5, 1.2, 0)
    norms = np.linalg.norm(flow, axis=2)
    median = np.median(flow.reshape(-1, 2), axis=0)
    residual = float(np.median(norms)) - float(global_motion.get("magnitude", 0.0))
    local_motion = {
        "dense_median_dx": round(float(median[0]), 4),
        "dense_median_dy": round(float(median[1]), 4),
        "dense_motion_energy": round(float(np.mean(norms)), 4),
        "local_motion_ratio": round(float(np.mean(norms > max(1.0, np.mean(norms) * 1.8))), 4),
        "global_residual": round(residual, 4),
        "dominant_motion_source": classify_motion_source(global_motion, float(np.mean(norms))),
    }
    return {"global_motion": global_motion, "local_motion": local_motion, "shake_score": round(abs(residual), 4)}


def window_motion_descriptor(frames: list[np.ndarray]) -> dict[str, Any]:
    if len(frames) < 2:
        return {"dominant_motion_source": "uncertain", "motion_class": "uncertain", "confidence": 0.0, "vector": [0.0, 0.0], "magnitude": 0.0}
    pair = estimate_motion_pair(frames[0], frames[-1])
    gm = pair["global_motion"]
    return {
        "dominant_motion_source": pair["local_motion"]["dominant_motion_source"],
        "motion_class": classify_motion(gm, pair["local_motion"]),
        "confidence": gm.get("confidence", 0.0),
        "vector": [gm.get("dx", 0.0), gm.get("dy", 0.0)],
        "magnitude": gm.get("magnitude", 0.0),
        "farneback_used_for_residual": True,
        "local_motion": pair["local_motion"],
    }


def detect_abab_ranges(frames: list[np.ndarray], times: list[int], *, near_threshold: float = 1.2, far_threshold: float = 4.0) -> list[dict[str, Any]]:
    ranges = []
    for i in range(3, len(frames)):
        a = _frame_diff(frames[i], frames[i - 2])
        b = _frame_diff(frames[i - 1], frames[i - 3])
        c = _frame_diff(frames[i], frames[i - 1])
        if a <= near_threshold and b <= near_threshold and c >= far_threshold:
            ranges.append({"start_ms": times[i - 3], "end_ms": times[i], "artifact": "ABAB_ALTERNATING_FRAME_PATTERN", "confidence": 0.75})
    return _merge_ranges(ranges)


def artifact_report_for_video(video_path: Path | str) -> dict[str, Any]:
    asset = analyze_video_file(video_path, sample_fps=6.0)
    summary = asset["artifact_summary"]
    hard_artifacts = bool(asset["abab_frame_ranges"] or asset["duplicate_frame_ranges"])
    motion_risks = [item for item in asset["glitch_risk_ranges"] if item.get("artifact") == "high_frequency_motion_reversal"]
    return {
        "video_path": str(video_path),
        "exact_duplicate_ranges": asset["duplicate_frame_ranges"],
        "near_duplicate_ranges": asset["freeze_ranges"],
        "abab_frame_ranges": asset["abab_frame_ranges"],
        "glitch_risk_ranges": asset["glitch_risk_ranges"],
        "motion_risk_ranges": motion_risks,
        "temporal_artifact_detected": hard_artifacts,
        "temporal_risk_detected": bool(motion_risks),
        "summary": summary,
    }


def calibrate_thresholds(output_dir: Path | str, positive_reports: Iterable[dict[str, Any]], negative_reports: Iterable[dict[str, Any]]) -> dict[str, Any]:
    positives = list(positive_reports)
    negatives = list(negative_reports)
    pos_blur = [asset["artifact_summary"]["median_blur"] for asset in positives if asset.get("artifact_summary")]
    neg_blur = [asset["artifact_summary"]["median_blur"] for asset in negatives if asset.get("artifact_summary")]
    pos_motion = [asset["artifact_summary"]["median_motion"] for asset in positives if asset.get("artifact_summary")]
    neg_glitch = [len(asset.get("glitch_risk_ranges", [])) + len(asset.get("abab_frame_ranges", [])) for asset in negatives]
    blur_floor = float(np.percentile(pos_blur, 10)) if pos_blur else 0.0
    motion_spike_floor = float(np.percentile(pos_motion, 95)) if pos_motion else 0.0
    payload = {
        "spec_version": "P12W-v1",
        "threshold_method": "P12T/P12U robust percentile calibration, not fixed magic constants",
        "positive_sample_count": len(positives),
        "negative_sample_count": len(negatives),
        "thresholds": {
            "blur_soft_floor": round(blur_floor, 4),
            "motion_spike_soft_floor": round(motion_spike_floor, 4),
            "abab_any_range_reject": True,
            "glitch_any_range_reject": True,
        },
        "samples": {
            "positive": [_sample_record(item) for item in positives],
            "negative": [_sample_record(item) for item in negatives],
        },
        "false_positive_risk": "medium: noisy handheld source can resemble glitches; VLM and source/render comparison remain required",
        "false_negative_risk": "medium: low-density scan may miss very short artifacts; final video scan uses denser sampling",
    }
    write_json(Path(output_dir) / "cv_threshold_calibration.json", payload)
    return payload


def ffprobe_json(path: Path | str) -> dict[str, Any]:
    completed = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)], capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr[-500:])
    return json.loads(completed.stdout)


def write_json(path: Path | str, payload: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(output)
    return output


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def classify_motion_source(global_motion: dict[str, Any], dense_energy: float) -> str:
    mag = float(global_motion.get("magnitude", 0.0))
    conf = float(global_motion.get("confidence", 0.0))
    if mag < 0.5 and dense_energy < 0.8:
        return "static"
    if conf >= 0.65 and mag >= 1.0 and dense_energy <= max(1.2, mag * 1.8):
        return "camera_motion"
    if mag < 1.0 and dense_energy >= 1.2:
        return "subject_motion"
    if mag >= 1.0 and dense_energy >= 1.2:
        return "mixed_motion"
    return "uncertain"


def classify_motion(global_motion: dict[str, Any], local_motion: dict[str, Any]) -> str:
    if local_motion.get("dominant_motion_source") == "static":
        return "static"
    if float(global_motion.get("confidence", 0.0)) < 0.60:
        return "uncertain"
    dx = float(global_motion.get("dx", 0.0))
    dy = float(global_motion.get("dy", 0.0))
    if abs(dx) > abs(dy) * 1.5:
        return "pan_right" if dx > 0 else "pan_left"
    if abs(dy) > abs(dx) * 1.5:
        return "tilt_down" if dy > 0 else "tilt_up"
    return "mixed_motion"


def _gray_resize(frame: np.ndarray, width: int = 320) -> np.ndarray:
    h, w = frame.shape[:2]
    height = max(1, int(round(h * width / max(w, 1))))
    resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    return cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY) if len(resized.shape) == 3 else resized


def _tenengrad(frame: np.ndarray) -> float:
    gx = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
    gy = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)
    return float(np.mean(gx * gx + gy * gy))


def _exposure(frame: np.ndarray) -> dict[str, Any]:
    hist = cv2.calcHist([frame], [0], None, [256], [0, 256]).flatten()
    total = float(np.sum(hist)) or 1.0
    return {
        "mean_luma": round(float(np.mean(frame)), 4),
        "highlight_clip_ratio": round(float(np.sum(hist[245:]) / total), 6),
        "shadow_clip_ratio": round(float(np.sum(hist[:10]) / total), 6),
        "midtone_ratio": round(float(np.sum(hist[32:224]) / total), 6),
    }


def _frame_diff(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean(np.abs(a.astype(np.int16) - b.astype(np.int16))))


def _duplicate_ranges(frames: list[np.ndarray], times: list[int]) -> list[dict[str, Any]]:
    ranges = []
    for i in range(1, len(frames)):
        if hashlib.md5(frames[i].tobytes()).digest() == hashlib.md5(frames[i - 1].tobytes()).digest():
            ranges.append({"start_ms": times[i - 1], "end_ms": times[i], "artifact": "exact_duplicate_frame", "confidence": 1.0})
    return _merge_ranges(ranges)


def _near_static_ranges(diffs: list[float], times: list[int], threshold: float = 0.8) -> list[dict[str, Any]]:
    ranges = []
    for i, diff in enumerate(diffs, start=1):
        if diff <= threshold:
            ranges.append({"start_ms": times[i - 1], "end_ms": times[i], "artifact": "near_duplicate_or_static", "confidence": 0.65})
    return _merge_ranges(ranges)


def _glitch_ranges(diffs: list[float], times: list[int], abab: list[dict[str, Any]], duplicates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranges = list(abab) + list(duplicates)
    if len(diffs) >= 4:
        median = float(np.median(diffs))
        mad = float(np.median(np.abs(np.asarray(diffs) - median))) or 1.0
        signs = np.sign(np.diff(diffs))
        for i in range(2, len(diffs)):
            z = abs(diffs[i] - median) / mad
            reversal = signs[i - 1] != 0 and signs[i - 2] != 0 and signs[i - 1] != signs[i - 2]
            if z > 8.0 and reversal:
                ranges.append({"start_ms": times[i - 1], "end_ms": times[i + 1] if i + 1 < len(times) else times[i], "artifact": "high_frequency_motion_reversal", "confidence": 0.7})
    return _merge_ranges(ranges)


def _merge_ranges(ranges: list[dict[str, Any]], gap_ms: int = 120) -> list[dict[str, Any]]:
    if not ranges:
        return []
    ordered = sorted(ranges, key=lambda item: item["start_ms"])
    merged = [dict(ordered[0])]
    for item in ordered[1:]:
        last = merged[-1]
        if item["start_ms"] <= last["end_ms"] + gap_ms and item["artifact"] == last["artifact"]:
            last["end_ms"] = max(last["end_ms"], item["end_ms"])
            last["confidence"] = max(last["confidence"], item["confidence"])
        else:
            merged.append(dict(item))
    return merged


def _technical_quality(blur: list[float], exposure: list[dict[str, Any]], diffs: list[float], duplicates: list[dict[str, Any]], glitches: list[dict[str, Any]]) -> dict[str, Any]:
    median_blur = float(np.median(blur)) if blur else 0.0
    median_motion = float(np.median(diffs)) if diffs else 0.0
    highlight = float(np.median([item["highlight_clip_ratio"] for item in exposure])) if exposure else 0.0
    shadow = float(np.median([item["shadow_clip_ratio"] for item in exposure])) if exposure else 0.0
    score = 82.0 + min(10.0, median_blur / 80.0) - min(20.0, (highlight + shadow) * 100.0) - len(glitches) * 8.0 - len(duplicates) * 5.0
    return {
        "median_blur": round(median_blur, 4),
        "median_motion": round(median_motion, 4),
        "exact_duplicate_run_count": len(duplicates),
        "glitch_range_count": len(glitches),
        "technical_quality_score": round(max(0.0, min(100.0, score)), 2),
        "reject_reason": "temporal_artifact" if glitches else "",
        "confidence": 0.82,
    }


def _curve(times: list[int], values: list[float], key: str) -> list[dict[str, Any]]:
    return [{"time_ms": times[i], key: round(float(value), 4)} for i, value in enumerate(values[: len(times)])]


def _rate_to_float(rate: str) -> float:
    if "/" in rate:
        a, b = rate.split("/", 1)
        return float(a) / max(float(b), 1e-6)
    return float(rate)


def _sample_record(asset: dict[str, Any]) -> dict[str, Any]:
    return {
        "sample_id": asset.get("source_video_id") or Path(str(asset.get("source_path", ""))).stem,
        "feature_values": asset.get("artifact_summary", {}),
        "calibration_result": "positive_reference" if not asset.get("glitch_risk_ranges") else "negative_reference",
    }


def _zero_global(source: str) -> dict[str, Any]:
    return {"dx": 0.0, "dy": 0.0, "magnitude": 0.0, "angle_deg": 0.0, "rotation_deg": 0.0, "scale": 1.0, "inlier_ratio": 0.0, "confidence": 0.0, "source": source}


def _empty_metrics() -> dict[str, Any]:
    return {
        "blur_curve": [],
        "tenengrad_curve": [],
        "exposure_curve": [],
        "highlight_clip_ratio": 0.0,
        "shadow_clip_ratio": 0.0,
        "motion_energy_curve": [],
        "global_motion_curve": [],
        "local_motion_curve": [],
        "shake_curve": [],
        "duplicate_frame_ranges": [],
        "freeze_ranges": [],
        "abab_frame_ranges": [],
        "glitch_risk_ranges": [],
        "motion_peak_ranges": [],
        "technical_quality_score": 0.0,
        "safe_crop_score": 0.0,
        "motion_descriptors": {},
        "artifact_summary": {"technical_quality_score": 0.0, "reject_reason": "no_frames", "confidence": 0.0},
    }
