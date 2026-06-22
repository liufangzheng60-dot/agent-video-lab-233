"""Director slate generation and GLM-4.6V storyboard judging for P12R."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


PROVIDER = "zhipu"
MODEL = "glm-4.6v"
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
STORYBOARD_JUDGE_GAP_THRESHOLD = 5.0


@dataclass(frozen=True)
class TimelineShot:
    role: str
    file: str
    source_start_ms: int
    duration_ms: int
    visual_start_ms: int
    visual_end_ms: int
    why: str
    shot_scale: str = "unknown"
    claim_evidence: str = ""
    action_complete: bool = True
    designed_hold_ms: int = 0
    camera_motion: str = "static"
    camera_motion_direction: str = "none"
    subject_motion_direction: str = "none"
    motion_energy: str = "medium"
    visual_hygiene_result: str = "unchecked"


@dataclass(frozen=True)
class DirectorSlate:
    variant_id: str
    slate_id: str
    strategy: str
    shots: list[TimelineShot]
    local_score: float
    local_reasons: list[str]
    soft_penalties: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant_id": self.variant_id,
            "slate_id": self.slate_id,
            "strategy": self.strategy,
            "shots": [asdict(shot) for shot in self.shots],
            "local_score": self.local_score,
            "local_reasons": self.local_reasons,
            "soft_penalties": self.soft_penalties,
        }


def should_call_storyboard_judge(top_two: Sequence[DirectorSlate], *, gap_threshold: float = STORYBOARD_JUDGE_GAP_THRESHOLD) -> bool:
    if len(top_two) < 2:
        return False
    return abs(float(top_two[0].local_score) - float(top_two[1].local_score)) < gap_threshold


def select_slate_by_local_gap(slates: Sequence[DirectorSlate], *, gap_threshold: float = STORYBOARD_JUDGE_GAP_THRESHOLD) -> tuple[DirectorSlate, bool, float]:
    top_two = pick_top_two(slates)
    if len(top_two) == 1:
        return top_two[0], False, 999.0
    gap = round(float(top_two[0].local_score) - float(top_two[1].local_score), 2)
    return top_two[0], gap < gap_threshold, gap


def build_four_candidate_slates(
    variant_id: str,
    breath_groups: Sequence[dict[str, Any]],
    visual_plan: Sequence[dict[str, Any]],
    label_index: dict[str, dict[str, Any]] | None = None,
) -> list[DirectorSlate]:
    if len(visual_plan) < len(breath_groups):
        raise ValueError(f"{variant_id}: visual_plan must cover every breath group")
    label_index = label_index or {}
    strategies = [
        ("A", "grammar_baseline"),
        ("B", "rhythm_first"),
        ("C", "continuity_first"),
        ("D", "vlm_directed"),
    ]
    slates: list[DirectorSlate] = []
    for suffix, strategy in strategies:
        shots = _build_strategy_shots(strategy, breath_groups, visual_plan, label_index)
        score, reasons, penalties = score_candidate_slate(variant_id, strategy, shots, label_index)
        slates.append(
            DirectorSlate(
                variant_id=variant_id,
                slate_id=f"{variant_id}_{suffix}",
                strategy=strategy,
                shots=shots,
                local_score=score,
                local_reasons=reasons,
                soft_penalties=penalties,
            )
        )
    return slates


def pick_top_two(slates: Sequence[DirectorSlate]) -> list[DirectorSlate]:
    return sorted(slates, key=lambda item: item.local_score, reverse=True)[:2]


def judge_storyboards_with_glm(
    variant_id: str,
    top_two: Sequence[DirectorSlate],
    output_dir: Path | str,
    *,
    model: str = MODEL,
    provider: str = PROVIDER,
) -> dict[str, Any]:
    if provider != PROVIDER:
        raise ValueError("P12R requires provider=zhipu")
    if model != MODEL:
        raise ValueError("P12R requires model=glm-4.6v")
    api_key = os.environ.get("ZHIPU_API_KEY")
    if not api_key:
        raise RuntimeError("ZHIPU_API_KEY is required and no fallback key is allowed")
    payload = {
        "variant_id": variant_id,
        "provider": provider,
        "requested_model": model,
        "candidate_count": len(top_two),
        "candidates": [slate.to_dict() for slate in top_two],
        "instruction": (
            "You are the P12R/P12S Storyboard Judge. Choose the stronger vertical TikTok product-video slate. "
            "Prefer precise first-3-second hook, complete action, AV causality, 8-12s continuity for V2, "
            "and clear product evidence. Return strict JSON only with winner_slate_id, scores, reasons, "
            "aesthetic_score, continuity_score, hook_score, risk_notes."
        ),
    }
    try:
        from zai import ZhipuAiClient
    except Exception as exc:
        raise RuntimeError(f"zai-sdk import failed: {exc}") from exc
    client = ZhipuAiClient(api_key=api_key, base_url=BASE_URL)
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "Return JSON only. Do not select an unlisted slate."},
            {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
        ],
        temperature=0,
        do_sample=False,
        stream=False,
        thinking={"type": "disabled"},
    )
    response_model = getattr(response, "model", None) or getattr(response, "model_name", None)
    if response_model != model:
        raise RuntimeError(f"model fallback detected: requested={model}, response={response_model}")
    content = response.choices[0].message.content
    parsed = _parse_json_content(content)
    valid_ids = {slate.slate_id for slate in top_two}
    if parsed.get("winner_slate_id") not in valid_ids:
        parsed["winner_slate_id"] = top_two[0].slate_id
        parsed.setdefault("risk_notes", []).append("judge winner missing or invalid; used local top slate")
    usage = _usage_to_dict(getattr(response, "usage", None))
    result = {
        "provider": provider,
        "requested_model": model,
        "response_model": response_model,
        "variant_id": variant_id,
        "winner_slate_id": parsed["winner_slate_id"],
        "judge": parsed,
        "usage": usage,
    }
    write_json(Path(output_dir) / f"{variant_id}_storyboard_judge.json", result)
    return result


def build_visual_hygiene_review_payload(
    variant_id: str,
    slate: dict[str, Any],
    *,
    spec_version: str = "P12S-v1",
) -> dict[str, Any]:
    return {
        "spec_version": spec_version,
        "variant_id": variant_id,
        "task": "final candidate visual hygiene and kinematic fluency review",
        "rules": {
            "hand_default": "reject",
            "hook_hand_max_ms": 800,
            "transformation_hand_max_ms": 1500,
            "face_or_body": "hard_reject",
            "outcome_proof_transformation_must_include": ["completion", "settle"],
            "uncertain_result": "reject",
        },
        "slate": slate,
        "return_json_schema": {
            "visual_hygiene_result": "pass|reject|uncertain",
            "hand_present": "boolean",
            "human_face_present": "boolean",
            "human_body_present": "boolean",
            "hand_after_hook": "boolean",
            "allowed_hand_context": "opening_hook|product_transformation|none",
            "action_integrity_result": "pass|reject|uncertain",
            "motion_direction_result": "pass|soft_issue|reject",
            "visual_hygiene_reason": "string",
            "action_integrity_reason": "string",
            "risk_timecodes_ms": ["integer"]
        },
    }


def select_slate_after_judge(slates: Sequence[DirectorSlate], judge_result: dict[str, Any]) -> DirectorSlate:
    winner = str(judge_result.get("winner_slate_id") or "")
    by_id = {slate.slate_id: slate for slate in slates}
    if winner not in by_id:
        return sorted(slates, key=lambda item: item.local_score, reverse=True)[0]
    return by_id[winner]


def write_candidate_slates(output_dir: Path | str, variant_id: str, slates: Sequence[DirectorSlate], selected: DirectorSlate) -> None:
    payload = {
        "variant_id": variant_id,
        "candidate_count": len(slates),
        "selected_slate_id": selected.slate_id,
        "slates": [slate.to_dict() for slate in slates],
    }
    write_json(Path(output_dir) / f"{variant_id}_director_slates.json", payload)


def score_candidate_slate(
    variant_id: str,
    strategy: str,
    shots: Sequence[TimelineShot],
    label_index: dict[str, dict[str, Any]],
) -> tuple[float, list[str], list[str]]:
    score = 78.0
    reasons: list[str] = []
    penalties: list[str] = []
    first = shots[0]
    first_label = label_index.get(first.file, {})
    if first_label.get("dog_present") and first_label.get("product_present"):
        score += 6
        reasons.append("hook includes dog and product")
    if first.duration_ms <= 2800:
        score += 3
        reasons.append("first breath group is tight")
    if strategy == "rhythm_first":
        score += 3
        reasons.append("shot timing follows audio breath groups")
    if strategy == "continuity_first":
        score += 4
        reasons.append("continuity strategy protects complete action")
    if strategy == "vlm_directed":
        score += 4
        reasons.append("VLM label evidence weighted in selection")
    for prev, shot in zip(shots, shots[1:]):
        if prev.shot_scale == shot.shot_scale and shot.shot_scale != "unknown":
            score -= 1.5
            penalties.append(f"same shot scale soft penalty: {prev.role}->{shot.role}")
    if "V2" in variant_id and _covers_seconds(shots, 8000, 12000, same_file=True):
        score += 7
        reasons.append("8-12s continuity covered by one source chain")
    if "V3A" in variant_id and all(shot.duration_ms >= 1700 for shot in shots[1:4]):
        score += 5
        reasons.append("middle action no longer truncated")
    return round(max(0, min(100, score)), 2), reasons, penalties


def _build_strategy_shots(
    strategy: str,
    breath_groups: Sequence[dict[str, Any]],
    visual_plan: Sequence[dict[str, Any]],
    label_index: dict[str, dict[str, Any]],
) -> list[TimelineShot]:
    shots: list[TimelineShot] = []
    for index, group in enumerate(breath_groups):
        plan = dict(visual_plan[index])
        if strategy == "continuity_first" and plan.get("continuity_file"):
            plan["file"] = plan["continuity_file"]
            plan["source_start_ms"] = plan.get("continuity_start_ms", plan.get("source_start_ms", 0))
        elif strategy == "vlm_directed" and plan.get("vlm_file"):
            plan["file"] = plan["vlm_file"]
            plan["source_start_ms"] = plan.get("vlm_start_ms", plan.get("source_start_ms", 0))
        duration_ms = max(900, int(group["end_ms"]) - int(group["start_ms"]))
        visual_start_ms = int(group["start_ms"])
        if strategy == "rhythm_first":
            visual_start_ms = max(0, visual_start_ms - 80)
            duration_ms += 80
        label = label_index.get(str(plan["file"]), {})
        shots.append(
            TimelineShot(
                role=str(group["role"]),
                file=str(plan["file"]),
                source_start_ms=int(plan.get("source_start_ms", plan.get("start_ms", 0))),
                duration_ms=duration_ms,
                visual_start_ms=visual_start_ms,
                visual_end_ms=visual_start_ms + duration_ms,
                why=str(plan.get("why", "")),
                shot_scale=str(label.get("shot_scale", "unknown")),
                claim_evidence=str(label.get("claim_evidence", "")),
                action_complete=str(label.get("action_completeness", "")).lower() not in {"truncated", "hard_cut"},
                designed_hold_ms=int(plan.get("designed_hold_ms", 0) or 0),
                camera_motion=str(plan.get("camera_motion", label.get("camera_motion", "static"))),
                camera_motion_direction=str(plan.get("camera_motion_direction", label.get("camera_motion_direction", "none"))),
                subject_motion_direction=str(plan.get("subject_motion_direction", label.get("dog_motion_direction", "none"))),
                motion_energy=str(plan.get("motion_energy", "medium")),
                visual_hygiene_result=str(plan.get("visual_hygiene_result", "unchecked")),
            )
        )
    return _lock_shots_to_zero(shots)


def _lock_shots_to_zero(shots: Sequence[TimelineShot]) -> list[TimelineShot]:
    locked: list[TimelineShot] = []
    cursor = 0
    for shot in shots:
        locked.append(
            TimelineShot(
                role=shot.role,
                file=shot.file,
                source_start_ms=shot.source_start_ms,
                duration_ms=shot.duration_ms,
                visual_start_ms=cursor,
                visual_end_ms=cursor + shot.duration_ms,
                why=shot.why,
                shot_scale=shot.shot_scale,
                claim_evidence=shot.claim_evidence,
                action_complete=shot.action_complete,
                designed_hold_ms=shot.designed_hold_ms,
                camera_motion=shot.camera_motion,
                camera_motion_direction=shot.camera_motion_direction,
                subject_motion_direction=shot.subject_motion_direction,
                motion_energy=shot.motion_energy,
                visual_hygiene_result=shot.visual_hygiene_result,
            )
        )
        cursor += shot.duration_ms
    return locked


def _covers_seconds(shots: Sequence[TimelineShot], start_ms: int, end_ms: int, *, same_file: bool) -> bool:
    covering = [shot for shot in shots if shot.visual_start_ms <= start_ms and shot.visual_end_ms >= end_ms]
    if covering:
        return True
    if not same_file:
        return False
    overlap = [shot for shot in shots if shot.visual_end_ms > start_ms and shot.visual_start_ms < end_ms]
    return bool(overlap) and len({shot.file for shot in overlap}) == 1


def _parse_json_content(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.split("\n", 1)[1] if "\n" in text else text
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end >= start:
        text = text[start : end + 1]
    return json.loads(text)


def _usage_to_dict(usage: Any) -> dict[str, int]:
    if usage is None:
        return {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    if hasattr(usage, "model_dump"):
        return usage.model_dump()
    if isinstance(usage, dict):
        return dict(usage)
    return {
        "prompt_tokens": int(getattr(usage, "prompt_tokens", 0) or 0),
        "completion_tokens": int(getattr(usage, "completion_tokens", 0) or 0),
        "total_tokens": int(getattr(usage, "total_tokens", 0) or 0),
    }


def write_json(path: Path | str, payload: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(output)
    return output
