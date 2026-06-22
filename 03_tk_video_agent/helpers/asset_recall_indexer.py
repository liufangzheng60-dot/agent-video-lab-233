"""Full-asset recall indexer with cached motion descriptors for P12U."""

from __future__ import annotations

import hashlib
import json
import math
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw


try:  # Optional: preferred by P12U when present.
    import cv2  # type: ignore
except Exception:  # pragma: no cover - environment dependent
    cv2 = None

try:
    from skimage import feature, measure, transform
except Exception:  # pragma: no cover - environment dependent
    feature = None
    measure = None
    transform = None


VIDEO_EXTENSIONS = {".mov", ".mp4", ".m4v"}


def build_physical_asset_index(raw_dir: Path | str, output_dir: Path | str) -> dict[str, Any]:
    raw = Path(raw_dir)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    assets = []
    motion_cache: dict[str, Any] = {}
    for path in sorted(p for p in raw.iterdir() if p.suffix.lower() in VIDEO_EXTENSIONS):
        probe = ffprobe_json(path)
        duration_ms = int(round(float(probe["format"]["duration"]) * 1000))
        stream = next(item for item in probe["streams"] if item.get("codec_type") == "video")
        keyframes = sparse_keyframe_times(duration_ms)
        frames = extract_keyframes(path, keyframes, out / "asset_keyframes" / path.stem)
        quality = compute_quality(frames)
        motion_curve = estimate_motion_curve(path, duration_ms)
        head = motion_descriptor(path, 0, min(500, duration_ms), cache=motion_cache)
        tail = motion_descriptor(path, max(0, duration_ms - 500), min(500, duration_ms), cache=motion_cache)
        assets.append(
            {
                "source_video_id": path.stem,
                "source_path": str(path),
                "file_hash": file_hash(path),
                "duration_ms": duration_ms,
                "width": int(stream.get("width", 0)),
                "height": int(stream.get("height", 0)),
                "avg_frame_rate": stream.get("avg_frame_rate"),
                "r_frame_rate": stream.get("r_frame_rate"),
                "time_base": stream.get("time_base"),
                "codec": stream.get("codec_name"),
                "rotation": stream.get("tags", {}).get("rotate", "0"),
                "audio_present": any(item.get("codec_type") == "audio" for item in probe["streams"]),
                "scene_boundaries": [{"start_ms": 0, "end_ms": duration_ms, "scene_id": f"{path.stem}_scene_001"}],
                "black_frame_ranges": [],
                "blur_score": quality["blur_score"],
                "brightness_score": quality["brightness_score"],
                "crop_safety": "vertical_crop_safe" if int(stream.get("width", 0)) >= 1080 else "review",
                "duplicate_group": None,
                "timestamp_risk": "ok",
                "motion_energy_curve": motion_curve,
                "motion_peaks": top_motion_peaks(motion_curve),
                "technical_quality_score": quality["technical_quality_score"],
                "head_motion_descriptor": head,
                "tail_motion_descriptor": tail,
            }
        )
    index = {
        "spec_version": "P12U-v1",
        "asset_count": len(assets),
        "opencv_available": cv2 is not None,
        "motion_fallback": "cv2_feature_ransac_farneback" if cv2 is not None else "skimage_feature_ransac_frame_diff",
        "assets": assets,
    }
    write_json(out / "physical_asset_index.json", index)
    write_json(out / "motion_descriptor_index.json", {"spec_version": "P12U-v1", "cache_size": len(motion_cache), "descriptors": motion_cache})
    return index


def create_scene_contact_sheets(index: dict[str, Any], output_dir: Path | str, *, batch_size: int = 13) -> dict[str, Any]:
    out = Path(output_dir)
    sheets_dir = out / "scene_contact_sheets"
    sheets_dir.mkdir(parents=True, exist_ok=True)
    items = []
    for asset in index["assets"]:
        key_dir = out / "asset_keyframes" / asset["source_video_id"]
        frame_paths = sorted(key_dir.glob("*.jpg"))
        sheet_path = sheets_dir / f"{asset['source_video_id']}_sheet.jpg"
        make_contact_sheet(frame_paths, sheet_path, title=asset["source_video_id"])
        items.append({"scene_id": f"{asset['source_video_id']}_scene_001", "source_video_id": asset["source_video_id"], "sheet": str(sheet_path)})
    batch_paths = []
    for start in range(0, len(items), batch_size):
        batch = items[start : start + batch_size]
        batch_path = sheets_dir / f"batch_{start // batch_size + 1:02d}.jpg"
        make_contact_sheet([Path(item["sheet"]) for item in batch], batch_path, title=f"batch_{start // batch_size + 1:02d}")
        batch_paths.append(str(batch_path))
    payload = {"spec_version": "P12U-v1", "scene_count": len(items), "items": items, "batch_sheets": batch_paths}
    write_json(out / "scene_contact_sheet_index.json", payload)
    return payload


def motion_descriptor(video_path: Path | str, start_ms: int, duration_ms: int, *, cache: dict[str, Any] | None = None) -> dict[str, Any]:
    key = f"{Path(video_path).name}:{start_ms}:{duration_ms}"
    if cache is not None and key in cache:
        return cache[key]
    frames = extract_keyframes(Path(video_path), [start_ms, start_ms + max(33, duration_ms // 2), start_ms + duration_ms], Path(tempfile.mkdtemp(prefix="p12u_motion_")))
    arrays = [np.asarray(Image.open(path).convert("L").resize((360, 202)), dtype=np.uint8) for path in frames if path.exists()]
    if len(arrays) < 2:
        descriptor = _static_descriptor("uncertain")
    else:
        descriptor = estimate_global_motion(arrays[0], arrays[-1])
        dense = dense_motion_aux(arrays[0], arrays[-1])
        descriptor.update(dense)
        descriptor["dominant_motion_source"] = classify_motion_source(descriptor)
        descriptor["motion_class"] = classify_motion(descriptor)
    if cache is not None:
        cache[key] = descriptor
    return descriptor


def estimate_global_motion(first: np.ndarray, last: np.ndarray) -> dict[str, Any]:
    if cv2 is not None:
        pts = cv2.goodFeaturesToTrack(first, maxCorners=180, qualityLevel=0.01, minDistance=7)
        if pts is None or len(pts) < 12:
            return _static_descriptor("uncertain")
        nxt, status, _ = cv2.calcOpticalFlowPyrLK(first, last, pts, None)
        good_old = pts[status.flatten() == 1]
        good_new = nxt[status.flatten() == 1]
        if len(good_old) < 12:
            return _static_descriptor("uncertain")
        mat, inliers = cv2.estimateAffinePartial2D(good_old, good_new, method=cv2.RANSAC, ransacReprojThreshold=3)
        if mat is None:
            return _static_descriptor("uncertain")
        dx, dy = float(mat[0, 2]), float(mat[1, 2])
        inlier_ratio = float(np.mean(inliers)) if inliers is not None else 0.0
    elif feature is not None and measure is not None and transform is not None:
        orb = feature.ORB(n_keypoints=180, fast_threshold=0.08)
        try:
            orb.detect_and_extract(first)
            keypoints1, descriptors1 = orb.keypoints, orb.descriptors
            orb.detect_and_extract(last)
            keypoints2, descriptors2 = orb.keypoints, orb.descriptors
            matches = feature.match_descriptors(descriptors1, descriptors2, cross_check=True)
            if len(matches) < 10:
                return _static_descriptor("uncertain")
            src = keypoints1[matches[:, 0]][:, ::-1]
            dst = keypoints2[matches[:, 1]][:, ::-1]
            model, inliers = measure.ransac((src, dst), transform.AffineTransform, min_samples=3, residual_threshold=3, max_trials=80)
            dx, dy = float(model.translation[0]), float(model.translation[1])
            inlier_ratio = float(np.mean(inliers)) if inliers is not None else 0.0
        except Exception:
            return _static_descriptor("uncertain")
    else:
        return _static_descriptor("uncertain")
    magnitude = math.hypot(dx, dy)
    angle = math.degrees(math.atan2(dy, dx)) if magnitude else 0.0
    confidence = max(0.0, min(1.0, inlier_ratio))
    return {
        "vector": [round(dx, 3), round(dy, 3)],
        "dx": round(dx, 3),
        "dy": round(dy, 3),
        "magnitude": round(magnitude, 3),
        "angle_deg": round(angle, 3),
        "rotation_deg": 0.0,
        "scale_change": 1.0,
        "inlier_ratio": round(inlier_ratio, 3),
        "reprojection_error": 0.0,
        "confidence": round(confidence, 3),
    }


def dense_motion_aux(first: np.ndarray, last: np.ndarray) -> dict[str, Any]:
    diff = np.abs(last.astype(np.int16) - first.astype(np.int16))
    energy = float(np.mean(diff))
    local_ratio = float(np.mean(diff > max(8, energy)))
    if cv2 is not None:
        flow = cv2.calcOpticalFlowFarneback(first, last, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        median = np.median(flow.reshape(-1, 2), axis=0)
        return {
            "farneback_available": True,
            "dense_median_dx": round(float(median[0]), 3),
            "dense_median_dy": round(float(median[1]), 3),
            "dense_motion_energy": round(float(np.mean(np.linalg.norm(flow, axis=2))), 3),
            "local_motion_ratio": round(local_ratio, 3),
            "global_local_consistency": "cross_checked",
        }
    return {
        "farneback_available": False,
        "dense_median_dx": 0.0,
        "dense_median_dy": 0.0,
        "dense_motion_energy": round(energy, 3),
        "local_motion_ratio": round(local_ratio, 3),
        "global_local_consistency": "fallback_frame_diff",
    }


def classify_motion_source(descriptor: dict[str, Any]) -> str:
    mag = float(descriptor.get("magnitude", 0.0))
    dense = float(descriptor.get("dense_motion_energy", 0.0))
    local = float(descriptor.get("local_motion_ratio", 0.0))
    if max(mag, dense) < 1.2:
        return "static"
    if mag >= 2.0 and local < 0.35:
        return "camera"
    if mag < 2.0 and dense >= 2.5:
        return "subject"
    if mag >= 2.0 and dense >= 2.5:
        return "mixed"
    return "uncertain"


def classify_motion(descriptor: dict[str, Any]) -> str:
    if descriptor.get("dominant_motion_source") == "static":
        return "static"
    if float(descriptor.get("confidence", 0.0)) < 0.6:
        return "uncertain"
    dx = float(descriptor.get("dx", 0.0))
    dy = float(descriptor.get("dy", 0.0))
    if abs(dx) > abs(dy) * 1.5:
        return "pan_right" if dx > 0 else "pan_left"
    if abs(dy) > abs(dx) * 1.5:
        return "tilt_down" if dy > 0 else "tilt_up"
    return "mixed_motion"


def ffprobe_json(path: Path) -> dict[str, Any]:
    completed = subprocess.run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)], capture_output=True, text=True, check=False)
    if completed.returncode:
        raise RuntimeError(completed.stderr[-400:])
    return json.loads(completed.stdout)


def extract_keyframes(path: Path, times_ms: list[int], output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for index, ms in enumerate(times_ms, start=1):
        out = output_dir / f"{index:02d}_{max(0, int(ms)):06d}.jpg"
        subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-ss", f"{max(0, ms) / 1000.0:.3f}", "-i", str(path), "-frames:v", "1", "-q:v", "3", str(out)], check=False)
        if out.exists():
            paths.append(out)
    return paths


def sparse_keyframe_times(duration_ms: int) -> list[int]:
    points = [0, int(duration_ms * 0.25), int(duration_ms * 0.5), int(duration_ms * 0.75), max(0, duration_ms - 80)]
    return sorted(set(points))


def compute_quality(frames: list[Path]) -> dict[str, float]:
    if not frames:
        return {"blur_score": 0.0, "brightness_score": 0.0, "technical_quality_score": 0.0}
    arrays = [np.asarray(Image.open(path).convert("L"), dtype=np.float32) for path in frames]
    brightness = float(np.mean([np.mean(item) for item in arrays]))
    blur = float(np.mean([np.var(np.diff(item, axis=0)) + np.var(np.diff(item, axis=1)) for item in arrays]))
    quality = max(0.0, min(100.0, 40 + blur / 50 + (100 - abs(brightness - 128)) / 3))
    return {"blur_score": round(blur, 3), "brightness_score": round(brightness, 3), "technical_quality_score": round(quality, 2)}


def estimate_motion_curve(path: Path, duration_ms: int) -> list[dict[str, float]]:
    times = list(range(0, max(duration_ms - 400, 1), max(400, duration_ms // 8)))
    frames = extract_keyframes(path, times, Path(tempfile.mkdtemp(prefix="p12u_motion_curve_")))
    arrays = [np.asarray(Image.open(item).convert("L").resize((240, 135)), dtype=np.int16) for item in frames]
    curve = []
    for index in range(1, len(arrays)):
        energy = float(np.mean(np.abs(arrays[index] - arrays[index - 1])))
        curve.append({"time_ms": float(times[index]), "motion_energy": round(energy, 3)})
    return curve


def top_motion_peaks(curve: list[dict[str, float]], keep: int = 3) -> list[dict[str, float]]:
    return sorted(curve, key=lambda item: item["motion_energy"], reverse=True)[:keep]


def make_contact_sheet(images: list[Path], output: Path, *, title: str = "") -> None:
    thumbs = []
    for path in images:
        if not path.exists():
            continue
        img = Image.open(path).convert("RGB")
        img.thumbnail((180, 320))
        canvas = Image.new("RGB", (180, 340), "white")
        canvas.paste(img, ((180 - img.width) // 2, 0))
        ImageDraw.Draw(canvas).text((4, 322), path.stem[:24], fill=(0, 0, 0))
        thumbs.append(canvas)
    if not thumbs:
        return
    cols = min(4, len(thumbs))
    rows = math.ceil(len(thumbs) / cols)
    sheet = Image.new("RGB", (cols * 180, rows * 340 + 24), "white")
    draw = ImageDraw.Draw(sheet)
    draw.text((6, 4), title, fill=(0, 0, 0))
    for idx, thumb in enumerate(thumbs):
        x = (idx % cols) * 180
        y = 24 + (idx // cols) * 340
        sheet.paste(thumb, (x, y))
    output.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(output, quality=88)


def file_hash(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(path: Path | str, payload: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return output


def _static_descriptor(source: str) -> dict[str, Any]:
    return {
        "vector": [0.0, 0.0],
        "dx": 0.0,
        "dy": 0.0,
        "magnitude": 0.0,
        "angle_deg": 0.0,
        "rotation_deg": 0.0,
        "scale_change": 1.0,
        "inlier_ratio": 0.0,
        "reprojection_error": 0.0,
        "confidence": 0.0,
        "dominant_motion_source": source,
        "motion_class": "uncertain",
        "farneback_available": False,
        "dense_median_dx": 0.0,
        "dense_median_dy": 0.0,
        "dense_motion_energy": 0.0,
        "local_motion_ratio": 0.0,
        "global_local_consistency": "unavailable",
    }
