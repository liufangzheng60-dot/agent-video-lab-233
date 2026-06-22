"""Cinematic feature scoring for P12X-v2 global storyboard search."""

from __future__ import annotations

import math
from copy import deepcopy
from dataclasses import dataclass
from typing import Any


MOTION_CONTINUITY_DEFAULT_WEIGHT = 0.04
MOTION_CONTINUITY_MAX_WEIGHT = 0.06
LOW_MOTION_CONFIDENCE = 0.60


@dataclass(frozen=True)
class ScoreBundle:
    total: float
    components: dict[str, float]
    hard_reject: bool = False
    reject_reasons: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": round(self.total, 3),
            "components": {key: round(value, 3) for key, value in self.components.items()},
            "hard_reject": self.hard_reject,
            "reject_reasons": list(self.reject_reasons),
        }


class CinematicFeatureEngine:
    """Deterministic local scorer using cached P12W OpenCV perception data."""

    def __init__(
        self,
        perception_index: dict[str, Any],
        motion_index: dict[str, Any],
        exclusions: dict[str, Any] | None = None,
        verified_windows: list[dict[str, Any]] | None = None,
        *,
        motion_weight: float = MOTION_CONTINUITY_DEFAULT_WEIGHT,
    ) -> None:
        self.assets = {item["source_video_id"]: item for item in perception_index.get("assets", [])}
        self.motion_descriptors = motion_index.get("descriptors", {})
        self.exclusions = exclusions.get("intervals", []) if exclusions else []
        self.verified_windows = verified_windows or []
        self.motion_weight = min(float(motion_weight), MOTION_CONTINUITY_MAX_WEIGHT)

    def candidate_features(self, shot: dict[str, Any], role_hint: str | None = None) -> dict[str, Any]:
        shot = deepcopy(shot)
        asset_id = str(shot.get("file", "")).replace(".MOV", "")
        asset = self.assets.get(asset_id, {})
        head = self.motion_descriptors.get(asset_id, {}).get("head", {})
        tail = self.motion_descriptors.get(asset_id, {}).get("tail", {})
        role = str(role_hint or shot.get("role", ""))
        return {
            "clip_id": self.clip_id(shot),
            "source_video_id": asset_id,
            "role": role,
            "technical_quality": float(asset.get("technical_quality_score", 80.0) or 80.0),
            "safe_crop_score": float(asset.get("safe_crop_score", 100.0) or 100.0),
            "temporal_artifact": bool(asset.get("artifact_summary", {}).get("reject_reason")),
            "abab_count": len(asset.get("abab_frame_ranges", [])),
            "duplicate_count": len(asset.get("duplicate_frame_ranges", [])),
            "glitch_count": len(asset.get("glitch_risk_ranges", [])),
            "head_global_motion": head,
            "tail_global_motion": tail,
            "motion_source": tail.get("dominant_motion_source", "uncertain"),
            "motion_confidence": float(tail.get("confidence", 0.0) or 0.0),
            "motion_energy": float(tail.get("magnitude", 0.0) or 0.0),
            "shot_scale": str(shot.get("shot_scale", "medium")),
            "subject_position": str(shot.get("subject_motion_direction", "center")),
            "product_state": str(shot.get("product_state", "visible")),
            "dog_position": str(shot.get("dog_position", shot.get("subject_motion_direction", "center"))),
            "action_phase": self.action_phase(role),
            "farneback_used_for_residual_only": True,
            "camera_motion_method": "feature_points_sparse_lk_ransac_affine",
        }

    def node_score(self, shot: dict[str, Any], role_hint: str | None = None) -> ScoreBundle:
        features = self.candidate_features(shot, role_hint)
        reasons = self._hard_reject_reasons(shot, features)
        role = features["role"]
        components = {
            "narrative_role_fit": self._role_fit(role),
            "composition": self._composition_score(shot, features),
            "action_completeness": 100.0 if str(shot.get("action_completeness", "complete")) == "complete" else 35.0,
            "visual_hygiene": 100.0 if not reasons else 0.0,
            "claim_evidence": self._claim_evidence(role),
            "technical_quality": features["technical_quality"],
            "temporal_stability": max(0.0, 100.0 - features["abab_count"] * 60.0 - features["duplicate_count"] * 35.0 - features["glitch_count"] * 10.0),
            "crop_safety": features["safe_crop_score"],
            "owner_style_match": self._owner_style_match(shot),
            "novelty": 88.0 if shot.get("p12x_new_high_value") else 72.0,
        }
        weights = {
            "narrative_role_fit": 0.22,
            "composition": 0.18,
            "action_completeness": 0.16,
            "visual_hygiene": 0.14,
            "claim_evidence": 0.10,
            "technical_quality": 0.07,
            "temporal_stability": 0.05,
            "crop_safety": 0.04,
            "owner_style_match": 0.02,
            "novelty": 0.02,
        }
        total = sum(components[key] * weights[key] for key in weights)
        return ScoreBundle(0.0 if reasons else total, components, bool(reasons), tuple(reasons))

    def edge_score(self, previous: dict[str, Any], current: dict[str, Any]) -> ScoreBundle:
        prev_features = self.candidate_features(previous)
        cur_features = self.candidate_features(current)
        jump = self.jump_cut_risk(previous, current, prev_features, cur_features)
        motion = self.motion_continuity(prev_features, cur_features)
        components = {
            "narrative_state_transition": self._transition_fit(previous, current),
            "product_dog_state_continuity": 86.0,
            "composition_progression": 80.0 - max(0.0, jump["risk_score"] - 20.0) * 0.45,
            "audio_cut_anchor": 86.0,
            "shot_scale_function": self._shot_scale_function(previous, current, jump),
            "motion_continuity": motion["score"],
            "subject_entry_exit": 82.0 if not motion["severe_direction_conflict"] else 58.0,
            "source_reuse_risk": 100.0 - jump["source_reuse_penalty"],
            "jump_cut_risk": 100.0 - jump["risk_score"],
        }
        weights = {
            "narrative_state_transition": 0.18,
            "product_dog_state_continuity": 0.10,
            "composition_progression": 0.16,
            "audio_cut_anchor": 0.14,
            "shot_scale_function": 0.10,
            "motion_continuity": self.motion_weight,
            "subject_entry_exit": 0.08,
            "source_reuse_risk": 0.10,
            "jump_cut_risk": 0.10,
        }
        residual = 1.0 - sum(weights.values())
        weights["narrative_state_transition"] += max(0.0, residual)
        total = sum(components[key] * weights[key] for key in weights)
        return ScoreBundle(total, components, jump["hard_reject"], tuple(jump["reasons"]))

    def sequence_score(self, shots: list[dict[str, Any]], family: str) -> ScoreBundle:
        roles = [str(shot.get("role", "")) for shot in shots]
        coverage = self.coverage_score(roles)
        components = {
            "story_completeness": coverage["score"],
            "visual_coverage": min(100.0, 66.0 + len(set(roles)) * 5.5),
            "commercial_causality": self._causality_score(roles),
            "pacing": self._pacing_score(shots),
            "composition_arc": self._composition_arc_score(shots),
            "closure": 92.0 if any("closure" in role or "payoff" in role or "outcome" in role for role in roles[-2:]) else 62.0,
            "cross_video_diversity": 88.0 if family != "P12W Baseline" else 74.0,
            "owner_preference": 88.0 if family in {"Narrative-First", "Cinematic-Global"} else 82.0,
        }
        penalties = self.sequence_penalties(shots)
        weighted = (
            components["story_completeness"] * 0.15
            + components["visual_coverage"] * 0.20
            + components["commercial_causality"] * 0.18
            + components["pacing"] * 0.12
            + components["composition_arc"] * 0.10
            + components["closure"] * 0.10
            + components["cross_video_diversity"] * 0.07
            + components["owner_preference"] * 0.08
        )
        total = max(0.0, weighted - sum(penalties.values()))
        components.update({f"penalty_{key}": -value for key, value in penalties.items()})
        return ScoreBundle(total, components, not coverage["passed"], tuple(coverage["missing"]))

    def coverage_score(self, roles: list[str]) -> dict[str, Any]:
        joined = " ".join(roles)
        if any(role.startswith("V1") for role in roles):
            required = []
        elif "feature" in joined or "proof" in joined:
            required = ["feature", "proof"]
        elif "usage" in joined or "transformation" in joined:
            required = ["usage_or_transformation", "payoff_or_closure"]
        else:
            required = ["problem_or_hook", "outcome_or_closure"]
        missing = []
        if "feature" in required and "feature" not in joined:
            missing.append("feature")
        if "proof" in required and "proof" not in joined:
            missing.append("proof")
        if "usage_or_transformation" in required and not ("usage" in joined or "transformation" in joined):
            missing.append("usage_or_transformation")
        if "payoff_or_closure" in required and not ("payoff" in joined or "closure" in joined):
            missing.append("payoff_or_closure")
        if "problem_or_hook" in required and not ("pain" in joined or "hook" in joined):
            missing.append("problem_or_hook")
        if "outcome_or_closure" in required and not ("outcome" in joined or "closure" in joined):
            missing.append("outcome_or_closure")
        return {"passed": not missing, "missing": missing, "score": max(55.0, 100.0 - len(missing) * 22.0)}

    def motion_continuity(self, previous_features: dict[str, Any], current_features: dict[str, Any]) -> dict[str, Any]:
        prev_motion = previous_features.get("tail_global_motion", {})
        cur_motion = current_features.get("head_global_motion", {})
        prev_conf = float(prev_motion.get("confidence", 0.0) or 0.0)
        cur_conf = float(cur_motion.get("confidence", 0.0) or 0.0)
        if min(prev_conf, cur_conf) < LOW_MOTION_CONFIDENCE:
            return {
                "score": 0.0,
                "weighted_contribution": 0.0,
                "confidence": min(prev_conf, cur_conf),
                "low_confidence_zeroed": True,
                "direction_similarity": 0.0,
                "magnitude_compatibility": 0.0,
                "severe_direction_conflict": False,
            }
        prev_vec = prev_motion.get("vector") or [prev_motion.get("dx", 0.0), prev_motion.get("dy", 0.0)]
        cur_vec = cur_motion.get("vector") or [cur_motion.get("dx", 0.0), cur_motion.get("dy", 0.0)]
        similarity = _direction_similarity(prev_vec, cur_vec)
        prev_mag = float(prev_motion.get("magnitude", 0.0) or 0.0)
        cur_mag = float(cur_motion.get("magnitude", 0.0) or 0.0)
        magnitude = min(prev_mag, cur_mag) / max(prev_mag, cur_mag, 1e-6)
        source_ok = previous_features.get("motion_source") != "subject_motion" and current_features.get("motion_source") != "subject_motion"
        if similarity >= 0.75 and magnitude >= 0.60 and source_ok:
            score = 92.0
        elif similarity < -0.55:
            score = 58.0
        else:
            score = 74.0
        severe = similarity < -0.75 and magnitude >= 0.65 and source_ok
        return {
            "score": score,
            "weighted_contribution": round(score * self.motion_weight, 3),
            "confidence": min(prev_conf, cur_conf),
            "low_confidence_zeroed": False,
            "direction_similarity": round(similarity, 4),
            "magnitude_compatibility": round(magnitude, 4),
            "severe_direction_conflict": severe,
        }

    def jump_cut_risk(
        self,
        previous: dict[str, Any],
        current: dict[str, Any],
        previous_features: dict[str, Any] | None = None,
        current_features: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        previous_features = previous_features or self.candidate_features(previous)
        current_features = current_features or self.candidate_features(current)
        same_source = previous_features["source_video_id"] == current_features["source_video_id"]
        same_scale = str(previous.get("shot_scale", "")) == str(current.get("shot_scale", ""))
        window_gap = abs(
            float(current.get("source_start_ms", 0))
            - (float(previous.get("source_start_ms", 0)) + float(previous.get("source_duration_ms", previous.get("duration_ms", 0))))
        )
        close_window = same_source and window_gap < 700.0
        same_position = str(previous.get("subject_motion_direction", "")) == str(current.get("subject_motion_direction", ""))
        action_progress = str(previous.get("role")) != str(current.get("role"))
        risk = 0.0
        reasons: list[str] = []
        if same_source:
            risk += 12.0
            reasons.append("same_source")
        if close_window:
            risk += 18.0
            reasons.append("near_or_overlapping_source_window")
        if same_scale:
            risk += 6.0
            reasons.append("same_shot_scale_soft_only")
        if same_position:
            risk += 8.0
            reasons.append("similar_subject_position")
        if not action_progress:
            risk += 16.0
            reasons.append("no_action_progress")
        hard = same_source and close_window and same_scale and same_position and not action_progress
        return {
            "risk_score": min(100.0, risk),
            "hard_reject": hard,
            "reasons": reasons if hard else [],
            "same_shot_scale_is_not_auto_jump_cut": True,
            "source_reuse_penalty": 22.0 if same_source else 0.0,
        }

    def clip_id(self, shot: dict[str, Any]) -> str:
        start = int(round(float(shot.get("source_start_ms", 0))))
        duration = int(round(float(shot.get("source_duration_ms", shot.get("duration_ms", 0)))))
        return f"{str(shot.get('file', '')).replace('.MOV', '')}:{start}+{duration}:{shot.get('role')}"

    def action_phase(self, role: str) -> str:
        role = role.lower()
        if "hook" in role or "pain" in role:
            return "setup"
        if "feature" in role or "intervention" in role or "transformation" in role:
            return "change"
        if "proof" in role or "usage" in role:
            return "evidence"
        if "payoff" in role or "closure" in role or "outcome" in role:
            return "settle"
        return "uncertain"

    def _hard_reject_reasons(self, shot: dict[str, Any], features: dict[str, Any]) -> list[str]:
        reasons = []
        role = str(shot.get("role", "")).lower()
        hand_allowed = (
            bool(shot.get("hand_present"))
            and (
                ("hook" in role and float(shot.get("hand_duration_ms", shot.get("duration_ms", 0)) or 0) <= 800.0)
                or ("transformation" in role and float(shot.get("hand_duration_ms", shot.get("duration_ms", 0)) or 0) <= 1500.0)
            )
        )
        if (shot.get("hand_present") and not hand_allowed) or shot.get("human_face_present") or shot.get("human_body_present"):
            reasons.append("semantic_hygiene_fail")
        if features["abab_count"] or features["duplicate_count"]:
            reasons.append("temporal_artifact_fail")
        if str(shot.get("action_completeness", "complete")) != "complete":
            reasons.append("action_incomplete")
        start = float(shot.get("source_start_ms", 0))
        end = start + float(shot.get("source_duration_ms", shot.get("duration_ms", 0)))
        source = features["source_video_id"]
        for item in self.exclusions:
            if str(item.get("source_video_id")) != source or str(item.get("severity")) != "fatal":
                continue
            if self._contained_in_verified_window(source, start, end):
                continue
            overlap = min(end, float(item.get("end_ms", 0))) - max(start, float(item.get("start_ms", 0)))
            if overlap > 50:
                reasons.append(f"fatal_exclusion:{item.get('violation_type')}")
        return reasons

    def _contained_in_verified_window(self, source: str, start: float, end: float) -> bool:
        for item in self.verified_windows:
            if str(item.get("source_video_id")) != source:
                continue
            if start >= float(item.get("start_ms", 0)) - 1.0 and end <= float(item.get("end_ms", 0)) + 1.0:
                return True
        return False

    def _role_fit(self, role: str) -> float:
        role = role.lower()
        if any(token in role for token in ("hook", "pain", "feature", "proof", "usage", "payoff", "closure", "outcome", "transformation")):
            return 92.0
        return 75.0

    def _composition_score(self, shot: dict[str, Any], features: dict[str, Any]) -> float:
        base = 82.0
        if str(shot.get("shot_scale")) in {"medium", "close", "wide"}:
            base += 5.0
        if features["safe_crop_score"] >= 95:
            base += 4.0
        return min(100.0, base)

    def _claim_evidence(self, role: str) -> float:
        role = role.lower()
        if "proof" in role or "demonstration" in role:
            return 94.0
        if "feature" in role or "transformation" in role:
            return 88.0
        if "closure" in role or "payoff" in role or "outcome" in role:
            return 84.0
        return 76.0

    def _owner_style_match(self, shot: dict[str, Any]) -> float:
        if shot.get("p12x_owner_fix"):
            return 94.0
        if shot.get("p12w_replacement_of") or shot.get("p12x_new_high_value"):
            return 88.0
        return 82.0

    def _transition_fit(self, previous: dict[str, Any], current: dict[str, Any]) -> float:
        prev_phase = self.action_phase(str(previous.get("role", "")))
        cur_phase = self.action_phase(str(current.get("role", "")))
        order = {"setup": 0, "change": 1, "evidence": 2, "settle": 3, "uncertain": 1}
        if order[cur_phase] >= order[prev_phase]:
            return 92.0
        return 70.0

    def _shot_scale_function(self, previous: dict[str, Any], current: dict[str, Any], jump: dict[str, Any]) -> float:
        if str(previous.get("shot_scale", "")) == str(current.get("shot_scale", "")):
            return 82.0 if jump["risk_score"] < 35 else 68.0
        return 90.0

    def _causality_score(self, roles: list[str]) -> float:
        joined = " ".join(roles)
        if "proof" in joined and "feature" in joined:
            return 92.0
        if "pain" in joined and ("outcome" in joined or "closure" in joined):
            return 90.0
        if ("usage" in joined or "transformation" in joined) and ("payoff" in joined or "closure" in joined):
            return 91.0
        return 78.0

    def _pacing_score(self, shots: list[dict[str, Any]]) -> float:
        count = len(shots)
        if 5 <= count <= 7:
            return 90.0
        return max(60.0, 92.0 - abs(count - 6) * 10.0)

    def _composition_arc_score(self, shots: list[dict[str, Any]]) -> float:
        scales = [str(shot.get("shot_scale", "medium")) for shot in shots]
        return 90.0 if len(set(scales)) >= 2 else 78.0

    def sequence_penalties(self, shots: list[dict[str, Any]]) -> dict[str, float]:
        source_counts: dict[str, int] = {}
        for shot in shots:
            source_counts[str(shot.get("file"))] = source_counts.get(str(shot.get("file")), 0) + 1
        return {
            "over_editing": 6.0 if len(shots) > 7 else 0.0,
            "repeated_information": 4.0 * sum(max(0, count - 2) for count in source_counts.values()),
            "source_concentration": 5.0 if max(source_counts.values(), default=0) >= 3 else 0.0,
            "state_regression": 0.0,
        }


def _direction_similarity(first: list[Any], second: list[Any]) -> float:
    ax, ay = float(first[0]), float(first[1])
    bx, by = float(second[0]), float(second[1])
    amag = math.hypot(ax, ay)
    bmag = math.hypot(bx, by)
    if amag < 1e-6 or bmag < 1e-6:
        return 0.0
    return (ax * bx + ay * by) / (amag * bmag)
