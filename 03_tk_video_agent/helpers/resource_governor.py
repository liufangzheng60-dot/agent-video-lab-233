"""Laptop-safe resource governor for P12D preflight and benchmark."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


LAPTOP_SAFE_PROFILE = {
    "resource_profile": "laptop_safe",
    "max_concurrent_ffmpeg": 1,
    "ffmpeg_threads_default": 2,
    "ffmpeg_threads_max": 4,
    "max_python_workers": 2,
    "max_vlm_concurrency": 1,
    "max_tts_concurrency": 1,
    "timeouts_sec": {
        "ffprobe": 60,
        "qc_draft": 180,
        "vlm": 120,
        "segment": 600,
        "final_render": 1200,
        "tts": 180,
        "packaging": 600,
    },
}


@dataclass
class ResourceGovernor:
    """Small local governor; no queues, daemons, databases, or background workers."""

    repo_root: Path
    product: str
    material_batch: str
    profile: dict[str, Any] = field(default_factory=lambda: dict(LAPTOP_SAFE_PROFILE))

    def inspect_hardware(self) -> dict[str, Any]:
        total_memory, available_memory, memory_percent = _memory_status()
        disk_free_gb = shutil.disk_usage(self.repo_root).free / (1024**3)
        return {
            "cpu_logical_count": os.cpu_count() or 1,
            "total_memory": total_memory,
            "available_memory": available_memory,
            "memory_percent": memory_percent,
            "disk_free_gb": round(disk_free_gb, 2),
            "power_status": _power_status(),
            "active_batch_lock": self._lock_path().exists(),
            "active_ffmpeg_count": _process_count("ffmpeg"),
            "recommended_profile": self.profile["resource_profile"],
        }

    def preflight(self) -> dict[str, Any]:
        info = self.inspect_hardware()
        blockers: list[str] = []
        warnings: list[str] = []
        if info["disk_free_gb"] < 25:
            blockers.append("可用磁盘低于 25GB，禁止启动真实 Batch。")
        if info["memory_percent"] >= 90:
            blockers.append("内存使用率高于 90%，必须 checkpoint 后安全停止。")
        elif info["memory_percent"] >= 82:
            warnings.append("内存使用率高于 82%，后续任务需要暂停启动新子进程。")
        if info["power_status"] == "battery":
            blockers.append("检测到电池供电，禁止启动真实 Batch。")
        elif info["power_status"] == "unknown":
            warnings.append("无法可靠检测供电状态，真实 Batch 前需要 Owner 人工确认已接入电源。")
        if info["active_batch_lock"]:
            blockers.append("检测到 active batch lock，拒绝启动第二个 Runtime Harness。")
        return {
            **info,
            "can_start_lightweight_benchmark": not info["active_batch_lock"] and info["disk_free_gb"] >= 15 and info["power_status"] != "battery",
            "can_start_real_batch": not blockers,
            "blockers": blockers,
            "warnings": warnings,
            "profile": self.profile,
        }

    def wait_until_safe(self) -> dict[str, Any]:
        return self.inspect_hardware()

    def before_stage(self, stage: str) -> dict[str, Any]:
        report = self.preflight()
        report["stage"] = stage
        return report

    def before_subprocess(self, stage: str, timeout: int) -> dict[str, Any]:
        return {"stage": stage, "timeout": timeout, "profile": self.profile["resource_profile"]}

    def run_limited_subprocess(
        self,
        args: list[str],
        *,
        stage: str,
        timeout: int,
        cwd: Path | None = None,
    ) -> dict[str, Any]:
        started = time.monotonic()
        try:
            result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, timeout=timeout, check=False)
            return {
                "status": "pass" if result.returncode == 0 else "fail",
                "returncode": result.returncode,
                "elapsed_sec": round(time.monotonic() - started, 3),
                "stdout": result.stdout,
                "stderr": result.stderr,
                "stdout_tail": result.stdout[-1000:],
                "stderr_tail": result.stderr[-2000:],
                "timeout": False,
                "stage": stage,
            }
        except subprocess.TimeoutExpired as exc:
            return {
                "status": "timeout",
                "returncode": None,
                "elapsed_sec": round(time.monotonic() - started, 3),
                "stdout": exc.stdout or "" if isinstance(exc.stdout, str) else "",
                "stderr": exc.stderr or "" if isinstance(exc.stderr, str) else "",
                "stdout_tail": (exc.stdout or "")[-1000:] if isinstance(exc.stdout, str) else "",
                "stderr_tail": (exc.stderr or "")[-2000:] if isinstance(exc.stderr, str) else "",
                "timeout": True,
                "stage": stage,
            }

    def record_metrics(self) -> dict[str, Any]:
        return self.inspect_hardware()

    def sample_runtime_metrics(self) -> dict[str, Any]:
        memory = _memory_status()
        return {
            "cpu_percent": _cpu_percent(),
            "memory_percent": memory[2],
            "disk_free_gb": round(shutil.disk_usage(self.repo_root).free / (1024**3), 2),
            "ffmpeg_count": _process_count("ffmpeg"),
            "python_count": _process_count("python"),
            "created_at": time.time(),
        }

    def checkpoint_and_stop(self, reason: str) -> dict[str, Any]:
        return {"pipeline_status": "PAUSED_BY_RESOURCE_GOVERNOR", "reason": reason}

    def can_start_real_batch(self) -> bool:
        return self.preflight()["can_start_real_batch"]

    def _lock_path(self) -> Path:
        return self.repo_root / "products" / self.product / "outputs" / "agent_factory" / self.material_batch / "agent_run.lock"


def write_resource_reports(output_dir: Path, report: dict[str, Any]) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "resource_preflight_report.json"
    md_path = output_dir / "resource_preflight_report.md"
    profile_path = output_dir / "recommended_runtime_profile.json"
    json_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    profile_path.write_text(json.dumps(report["profile"], ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# 资源预检报告",
        "",
        f"- 推荐资源模式：{report['recommended_profile']}",
        f"- 可用磁盘：{report['disk_free_gb']} GB",
        f"- 内存使用率：{report['memory_percent']}%",
        f"- 供电状态：{report['power_status']}",
        f"- 活动批次锁：{report['active_batch_lock']}",
        f"- 当前 FFmpeg 进程数：{report['active_ffmpeg_count']}",
        f"- 是否允许轻量 benchmark：{report['can_start_lightweight_benchmark']}",
        f"- 是否允许真实 Batch：{report['can_start_real_batch']}",
        f"- 阻塞项：{'; '.join(report['blockers']) if report['blockers'] else '无'}",
        f"- 警告：{'; '.join(report['warnings']) if report['warnings'] else '无'}",
    ]
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": json_path, "markdown": md_path, "profile": profile_path}


def _memory_status() -> tuple[int | None, int | None, float]:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "Get-CimInstance Win32_OperatingSystem | Select-Object TotalVisibleMemorySize,FreePhysicalMemory | ConvertTo-Json"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        if result.returncode == 0 and result.stdout.strip():
            data = json.loads(result.stdout)
            total = int(data["TotalVisibleMemorySize"]) * 1024
            free = int(data["FreePhysicalMemory"]) * 1024
            percent = round((1 - free / total) * 100, 2) if total else 0.0
            return total, free, percent
    except Exception:
        pass
    return None, None, 0.0


def _power_status() -> str:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Battery | Select-Object -First 1 BatteryStatus | ConvertTo-Json)"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        text = result.stdout.strip()
        if not text:
            return "unknown"
        data = json.loads(text)
        status = int(data.get("BatteryStatus", 0))
        if status in {2, 6, 7, 8, 9}:
            return "ac_or_charging"
        if status in {1, 3, 4, 5}:
            return "battery"
    except Exception:
        return "unknown"
    return "unknown"


def _cpu_percent() -> float:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", "(Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return round(float(result.stdout.strip() or 0), 2)
    except Exception:
        return 0.0


def _process_count(name: str) -> int:
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", f"@(Get-Process | Where-Object {{$_.ProcessName -like '{name}*'}}).Count"],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
        return int(result.stdout.strip() or "0")
    except Exception:
        return 0
