"""Lightweight Owner preference ranking for P12U storyboard scoring."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_WEIGHTS = {
    "zero_transition_freeze": 1.0,
    "no_hand_intrusion": 0.95,
    "action_completion": 0.92,
    "flow_over_forced_brevity": 0.88,
    "semantic_evidence": 0.86,
    "visual_hygiene": 0.84,
    "home_lifestyle_feeling": 0.72,
    "avoid_showroom_feel": 0.70,
    "motion_continuity": 0.12,
}


def build_owner_preference_pairs() -> list[dict[str, Any]]:
    return [
        {"preferred": "P12P", "rejected": "P12D", "reasons": ["semantic_compiler", "commercial_story"]},
        {"preferred": "P12Q", "rejected": "P12P", "reasons": ["better_hook", "six_variant_control"]},
        {"preferred": "P12R", "rejected": "P12Q", "reasons": ["audio_sync", "breath_group_rhythm"]},
        {"preferred": "P12S", "rejected": "P12R", "reasons": ["visual_hygiene", "action_completion"]},
        {"preferred": "P12T", "rejected": "P12S", "reasons": ["zero_transition_freeze", "pts_zero", "single_cfr"]},
        {"preferred": "P12T_V1B", "rejected": "P12R_V1B", "reasons": ["no_hand_intrusion", "hook_retained"]},
        {"preferred": "complete_motion", "rejected": "forced_15_seconds", "reasons": ["flow_over_forced_brevity"]},
    ]


def score_owner_preference(features: dict[str, float | int | bool], weights: dict[str, float] | None = None) -> float:
    active = weights or DEFAULT_WEIGHTS
    score = 0.0
    total = 0.0
    for key, weight in active.items():
        if key not in features:
            continue
        value = features[key]
        numeric = 1.0 if value is True else 0.0 if value is False else float(value)
        score += numeric * weight
        total += weight
    return round((score / total) * 100.0, 2) if total else 0.0


def write_preference_outputs(output_dir: Path | str, weights: dict[str, float] | None = None) -> dict[str, str]:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    active = weights or DEFAULT_WEIGHTS
    pairs_path = out / "owner_preference_pairs.jsonl"
    with pairs_path.open("w", encoding="utf-8") as handle:
        for item in build_owner_preference_pairs():
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
    report_path = out / "owner_preference_weight_report.json"
    report_path.write_text(
        json.dumps(
            {
                "spec_version": "P12U-v1",
                "weights": active,
                "update_strategy": "lightweight_pairwise_preferences_no_hard_constraint_override",
                "updated_from_new_owner_feedback": False,
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"pairs": str(pairs_path), "report": str(report_path)}
