"""Beam-search storyboard optimizer with motion-aware soft edge scoring."""

from __future__ import annotations

import itertools
import json
from pathlib import Path
from typing import Any


MOTION_WEIGHT = 0.12
MOTION_WEIGHT_CEILING = 0.15


def motion_transition_score(prev: dict[str, Any], nxt: dict[str, Any], *, weight: float = MOTION_WEIGHT) -> dict[str, Any]:
    active_weight = min(float(weight), MOTION_WEIGHT_CEILING)
    tail = prev.get("tail_motion_descriptor", {})
    head = nxt.get("head_motion_descriptor", {})
    confidence = min(float(tail.get("confidence", 0.0) or 0.0), float(head.get("confidence", 0.0) or 0.0))
    if confidence < 0.60:
        return {
            "motion_match_score": 0.0,
            "confidence": confidence,
            "direction_similarity": 0.0,
            "ranking_effect": "zero_low_confidence",
            "weight": active_weight,
        }
    tv = tail.get("vector", [0.0, 0.0])
    hv = head.get("vector", [0.0, 0.0])
    dot = float(tv[0]) * float(hv[0]) + float(tv[1]) * float(hv[1])
    norm = ((float(tv[0]) ** 2 + float(tv[1]) ** 2) ** 0.5) * ((float(hv[0]) ** 2 + float(hv[1]) ** 2) ** 0.5)
    direction_similarity = dot / norm if norm else 0.0
    mag_tail = float(tail.get("magnitude", 0.0) or 0.0)
    mag_head = float(head.get("magnitude", 0.0) or 0.0)
    magnitude_compatibility = 1.0 - min(1.0, abs(mag_tail - mag_head) / max(mag_tail, mag_head, 1.0))
    semantic_ok = not bool(nxt.get("semantic_conflict", False))
    if direction_similarity >= 0.75 and magnitude_compatibility >= 0.60 and semantic_ok:
        raw = 4.0 + 6.0 * min(direction_similarity, magnitude_compatibility) * confidence
        effect = "reward_same_direction"
    elif direction_similarity <= -0.60 and confidence >= 0.80 and not nxt.get("spatial_reset", False):
        raw = -4.0 - 6.0 * abs(direction_similarity) * confidence
        effect = "penalty_direction_conflict"
    else:
        raw = 0.0
        effect = "neutral"
    return {
        "motion_match_score": round(raw * active_weight / MOTION_WEIGHT, 2),
        "confidence": round(confidence, 3),
        "direction_similarity": round(direction_similarity, 3),
        "magnitude_compatibility": round(magnitude_compatibility, 3),
        "ranking_effect": effect,
        "weight": active_weight,
    }


def edge_score(prev: dict[str, Any], nxt: dict[str, Any], *, family: str = "quality-first") -> dict[str, Any]:
    base = 72.0
    if prev.get("file") == nxt.get("file"):
        base -= 8.0
    if prev.get("shot_scale") != nxt.get("shot_scale"):
        base += 4.0
    if family == "continuity-first" and prev.get("file") != nxt.get("file"):
        base += 2.0
    motion = motion_transition_score(prev, nxt, weight=MOTION_WEIGHT if family == "motion-aware" else 0.08)
    total = max(0.0, min(100.0, base + motion["motion_match_score"]))
    return {"edge_score": round(total, 2), "base_score": round(base, 2), "motion_transition": motion}


def beam_search_storyboards(role_candidates: dict[str, list[dict[str, Any]]], roles: list[str], *, beam_width: int = 30, family: str = "quality-first") -> list[dict[str, Any]]:
    beams: list[dict[str, Any]] = [{"clips": [], "score": 0.0, "edges": []}]
    for role in roles:
        next_beams: list[dict[str, Any]] = []
        for beam in beams:
            for candidate in role_candidates.get(role, [])[:15]:
                if _violates_hard_constraints(beam["clips"], candidate):
                    continue
                score = beam["score"] + float(candidate.get("node_score", 0.0))
                edges = list(beam["edges"])
                if beam["clips"]:
                    edge = edge_score(beam["clips"][-1], candidate, family=family)
                    score += edge["edge_score"]
                    edges.append(edge)
                next_beams.append({"clips": beam["clips"] + [candidate], "score": round(score, 2), "edges": edges, "family": family})
        beams = sorted(next_beams, key=lambda item: item["score"], reverse=True)[:beam_width]
    return beams


def generate_storyboard_families(role_candidates: dict[str, list[dict[str, Any]]], roles: list[str]) -> list[dict[str, Any]]:
    all_storyboards: list[dict[str, Any]] = []
    for family in ["quality-first", "continuity-first", "motion-aware"]:
        all_storyboards.extend(beam_search_storyboards(role_candidates, roles, family=family))
    for index, storyboard in enumerate(sorted(all_storyboards, key=lambda item: item["score"], reverse=True), start=1):
        storyboard["storyboard_id"] = f"sb_{index:03d}_{storyboard.get('family', 'unknown')}"
    return sorted(all_storyboards, key=lambda item: item["score"], reverse=True)


def diversity_rerank(storyboards: list[dict[str, Any]], keep: int = 6) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    discarded = 0
    for storyboard in storyboards:
        files = [clip["file"] for clip in storyboard["clips"]]
        if any(_overlap_ratio(files, [clip["file"] for clip in existing["clips"]]) > 0.55 for existing in selected):
            discarded += 1
            continue
        selected.append(storyboard)
        if len(selected) >= keep:
            break
    return selected, {"kept": len(selected), "discarded_for_similarity": discarded}


def write_storyboard_reports(output_dir: Path | str, storyboards: list[dict[str, Any]], selected: list[dict[str, Any]], diversity_report: dict[str, Any]) -> None:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    (out / "beam_search_storyboards.json").write_text(json.dumps(storyboards[:60], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "diversity_rerank_report.json").write_text(json.dumps(diversity_report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _violates_hard_constraints(existing: list[dict[str, Any]], candidate: dict[str, Any]) -> bool:
    if candidate.get("hard_reject"):
        return True
    for clip in existing:
        if clip.get("file") == candidate.get("file") and _windows_overlap(clip, candidate):
            return True
    return False


def _windows_overlap(a: dict[str, Any], b: dict[str, Any]) -> bool:
    a0 = int(a.get("source_start_ms", 0))
    a1 = a0 + int(a.get("source_duration_ms", a.get("duration_ms", 0)))
    b0 = int(b.get("source_start_ms", 0))
    b1 = b0 + int(b.get("source_duration_ms", b.get("duration_ms", 0)))
    return max(a0, b0) < min(a1, b1)


def _overlap_ratio(left: list[str], right: list[str]) -> float:
    if not left:
        return 0.0
    return len(set(left) & set(right)) / len(set(left))
