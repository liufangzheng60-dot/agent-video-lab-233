from __future__ import annotations

import asyncio
import base64
import json
import math
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


def repo_root() -> Path:
    completed = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=False)
    if completed.returncode == 0 and completed.stdout.strip():
        return Path(completed.stdout.strip()).resolve()
    return Path(__file__).resolve().parents[1]


ROOT = repo_root()
sys.path.insert(0, str(ROOT / "03_tk_video_agent"))

from helpers.transition_freeze_detector import analyze_video_transitions  # noqa: E402
from helpers.vision_compiler.opencv_perception import artifact_report_for_video, estimate_motion_pair  # noqa: E402
from helpers.vision_compiler.portable_paths import data_root  # noqa: E402


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def check(cmd: list[str]) -> None:
    completed = run(cmd)
    if completed.returncode:
        raise RuntimeError(completed.stderr[-1000:] or completed.stdout[-1000:])


def ffprobe_json(path: Path) -> dict[str, Any]:
    completed = run(["ffprobe", "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    if completed.returncode:
        raise RuntimeError(completed.stderr[-1000:])
    return json.loads(completed.stdout)


def create_synthetic_video(path: Path, *, static: bool = False, freeze_tail: bool = False) -> None:
    import cv2
    import numpy as np

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".avi")
    writer = cv2.VideoWriter(str(tmp), cv2.VideoWriter_fourcc(*"MJPG"), 30.0, (540, 960))
    last = np.zeros((960, 540, 3), dtype=np.uint8)
    for i in range(90):
        frame = np.zeros((960, 540, 3), dtype=np.uint8)
        frame[:, :] = (20, 30, 45)
        x = 80 if static else 40 + i * 4
        y = 280 if static else 240 + int(math.sin(i / 8) * 40)
        cv2.rectangle(frame, (x, y), (x + 120, y + 90), (60, 180, 240), -1)
        cv2.circle(frame, (270, 700), 55, (230, 230, 230), -1)
        if freeze_tail and i > 72:
            frame = last.copy()
        last = frame.copy()
        writer.write(frame)
    writer.release()
    check(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(tmp), "-vf", "scale=540:960,setsar=1,fps=30", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", str(path)])
    tmp.unlink(missing_ok=True)


async def edge_tts_audio(path: Path) -> bool:
    import edge_tts

    communicate = edge_tts.Communicate("This is a portable desktop smoke test for the video agent.", "en-US-AvaNeural")
    await communicate.save(str(path))
    return path.exists() and path.stat().st_size > 1000


def first_pts_zero(path: Path) -> bool:
    completed = run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "packet=pts_time", "-of", "csv=p=0", "-read_intervals", "%+#1", str(path)])
    if completed.returncode:
        return False
    try:
        return abs(float(completed.stdout.strip().splitlines()[0])) < 0.001
    except Exception:
        return False


def vlm_smoke(report: dict[str, Any], sheet_path: Path) -> None:
    report["vlm_test_requested"] = bool(os.environ.get("ZHIPU_API_KEY"))
    report["vlm_ok"] = None
    if not report["vlm_test_requested"]:
        return
    from zai import ZhipuAiClient

    client = ZhipuAiClient(api_key=os.environ["ZHIPU_API_KEY"], timeout=60, max_retries=0)
    image_b64 = base64.b64encode(sheet_path.read_bytes()).decode("ascii")
    response = client.chat.completions.create(
        model="glm-4.6v",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Return JSON only: {\"smoke_ok\": true}. This is a synthetic image, not a product video."},
                    {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + image_b64}},
                ],
            }
        ],
        do_sample=False,
        stream=False,
        max_tokens=80,
        thinking={"type": "disabled"},
    )
    if getattr(response, "model", None) != "glm-4.6v":
        raise RuntimeError("VLM model fallback detected")
    report["vlm_ok"] = True
    usage = getattr(response, "usage", None)
    if usage is not None and hasattr(usage, "model_dump"):
        report["vlm_usage"] = usage.model_dump()


def main() -> int:
    out = data_root(create=True) / "synthetic_smoke" / "outputs"
    out.mkdir(parents=True, exist_ok=True)
    moving = out / "synthetic_motion.mp4"
    static = out / "synthetic_static.mp4"
    freeze = out / "synthetic_freeze_negative.mp4"
    segment = out / "segment_pts0_30fps.mp4"
    final = out / "synthetic_final_mux.mp4"
    audio = out / "edge_tts_smoke.mp3"
    sheet = out / "synthetic_contact_sheet.jpg"
    report_path = out / "desktop_smoke_report.json"

    report: dict[str, Any] = {"python_ok": True, "ffmpeg_ok": run(["ffmpeg", "-version"]).returncode == 0}
    try:
        import cv2
        import numpy as np

        report["opencv_backend_used"] = True
        report["opencv_version"] = cv2.__version__
        create_synthetic_video(moving)
        create_synthetic_video(static, static=True)
        create_synthetic_video(freeze, freeze_tail=True)
        report["synthetic_video_created"] = moving.exists() and static.exists() and freeze.exists()

        cap = cv2.VideoCapture(str(moving))
        ok1, f1 = cap.read()
        ok2, f2 = cap.read()
        cap.release()
        if not (ok1 and ok2):
            raise RuntimeError("OpenCV failed to decode synthetic video")
        g1 = cv2.cvtColor(f1, cv2.COLOR_BGR2GRAY)
        g2 = cv2.cvtColor(f2, cv2.COLOR_BGR2GRAY)
        report["frame_diff"] = float(np.mean(np.abs(g2.astype(np.int16) - g1.astype(np.int16))))
        report["laplacian"] = float(cv2.Laplacian(g1, cv2.CV_64F).var())
        motion = estimate_motion_pair(g1, g2)
        report["global_motion_estimation_ok"] = motion["global_motion"]["confidence"] >= 0
        flow = cv2.calcOpticalFlowFarneback(g1, g2, None, 0.5, 3, 15, 3, 5, 1.2, 0)
        report["optical_flow_ok"] = bool(flow.shape[:2] == g1.shape)

        freeze_artifacts = artifact_report_for_video(freeze)
        report["freeze_negative_sample_detected"] = bool(freeze_artifacts["near_duplicate_ranges"] or freeze_artifacts["exact_duplicate_ranges"])

        check(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(moving), "-filter_complex", "[0:v]trim=start=0:duration=2,setpts=PTS-STARTPTS,scale=540:960,setsar=1,fps=30,trim=start_frame=0:end_frame=60,setpts=PTS-STARTPTS,format=yuv420p[v]", "-map", "[v]", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-frames:v", "60", str(segment)])
        report["first_pts_zero"] = first_pts_zero(segment)
        probe = ffprobe_json(segment)
        stream = next(item for item in probe["streams"] if item.get("codec_type") == "video")
        report["single_cfr"] = stream.get("avg_frame_rate") == "30/1"

        report["edge_tts_ok"] = asyncio.run(edge_tts_audio(audio))
        check(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(segment), "-i", str(audio), "-filter_complex", "[1:a]atrim=0:2,asetpts=PTS-STARTPTS,aresample=async=1:first_pts=0[a]", "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "128k", str(final)])
        final_probe = ffprobe_json(final)
        v_stream = next(item for item in final_probe["streams"] if item.get("codec_type") == "video")
        report["pipeline_render_ok"] = final.exists() and int(v_stream["height"]) / int(v_stream["width"]) == 16 / 9
        transition = analyze_video_transitions(final, {"shots": [{"role": "synthetic", "file": moving.name, "source_start_ms": 0, "source_duration_ms": 2000, "visual_start_ms": 0, "visual_end_ms": 2000}]}, moving.parent)
        report["pipeline_introduced_freeze"] = transition["hard_reject_count"]
        video_ms = float(final_probe["format"]["duration"]) * 1000
        report["av_error_ms"] = abs(video_ms - 2000)
        check(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(final), "-vf", "fps=1,scale=180:320,tile=2x2", "-frames:v", "1", str(sheet)])
        vlm_smoke(report, sheet)
    except Exception as exc:
        report["error"] = str(exc)

    required = [
        "python_ok",
        "ffmpeg_ok",
        "opencv_backend_used",
        "edge_tts_ok",
        "synthetic_video_created",
        "optical_flow_ok",
        "freeze_negative_sample_detected",
        "pipeline_render_ok",
        "first_pts_zero",
        "single_cfr",
    ]
    report["overall_pass"] = all(bool(report.get(key)) for key in required) and report.get("pipeline_introduced_freeze") == 0 and float(report.get("av_error_ms", 9999)) <= 100
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"desktop_smoke_report": str(report_path), **report}, indent=2, ensure_ascii=False))
    return 0 if report["overall_pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
