"""Audio-first rhythm helpers for P12R review videos.

The module keeps WordBoundary data as timing evidence only. It builds edit
groups around semantic breath groups and confirms pauses with punctuation,
boundary gaps, and measured audio silence.
"""

from __future__ import annotations

import asyncio
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Sequence


PUNCTUATION_RE = re.compile(r"[.!?,;:]$")
WORD_RE = re.compile(r"[A-Za-z0-9']+")
DEFAULT_VOICE = "en-US-AvaNeural"
TAIL_REVERB_MIN_MS = 150
TAIL_REVERB_MAX_MS = 400


@dataclass(frozen=True)
class NarrationSegment:
    role: str
    text: str
    designed_pause_ms: int = 0


@dataclass(frozen=True)
class WordBoundary:
    text: str
    start_ms: int
    duration_ms: int

    @property
    def end_ms(self) -> int:
        return self.start_ms + self.duration_ms


@dataclass(frozen=True)
class ConfirmedPause:
    after_role: str
    start_ms: int
    end_ms: int
    duration_ms: int
    punctuation: bool
    boundary_gap_ms: int
    audio_silence_ms: int
    confirmed: bool


@dataclass(frozen=True)
class BreathGroup:
    role: str
    text: str
    start_ms: int
    end_ms: int
    words: list[WordBoundary]
    punctuation_pause_confirmed_ms: int = 0

    @property
    def duration_ms(self) -> int:
        return self.end_ms - self.start_ms


@dataclass(frozen=True)
class AudioAlignment:
    variant_id: str
    voice: str
    text: str
    audio_path: str
    duration_ms: int
    last_word_end_ms: int
    tail_silence_ms: int
    max_internal_silence_ms: int
    words: list[WordBoundary]
    silences: list[dict[str, int]]
    pauses: list[ConfirmedPause]
    breath_groups: list[BreathGroup]

    def to_dict(self) -> dict[str, Any]:
        return {
            "variant_id": self.variant_id,
            "voice": self.voice,
            "text": self.text,
            "audio_path": self.audio_path,
            "duration_ms": self.duration_ms,
            "last_word_end_ms": self.last_word_end_ms,
            "tail_silence_ms": self.tail_silence_ms,
            "max_internal_silence_ms": self.max_internal_silence_ms,
            "words": [asdict(item) for item in self.words],
            "silences": self.silences,
            "pauses": [asdict(item) for item in self.pauses],
            "breath_groups": [
                {
                    "role": group.role,
                    "text": group.text,
                    "start_ms": group.start_ms,
                    "end_ms": group.end_ms,
                    "duration_ms": group.duration_ms,
                    "punctuation_pause_confirmed_ms": group.punctuation_pause_confirmed_ms,
                    "words": [asdict(item) for item in group.words],
                }
                for group in self.breath_groups
            ],
        }


def normalize_segments(segments: Sequence[dict[str, Any] | NarrationSegment]) -> list[NarrationSegment]:
    normalized: list[NarrationSegment] = []
    for item in segments:
        if isinstance(item, NarrationSegment):
            normalized.append(item)
        else:
            normalized.append(
                NarrationSegment(
                    role=str(item["role"]),
                    text=str(item["text"]).strip(),
                    designed_pause_ms=int(item.get("designed_pause_ms", 0) or 0),
                )
            )
    if not normalized:
        raise ValueError("at least one narration segment is required")
    return normalized


def join_segments_for_tts(segments: Sequence[NarrationSegment]) -> str:
    return " ".join(segment.text.strip() for segment in segments if segment.text.strip())


async def synthesize_edge_tts_with_boundaries(
    text: str,
    audio_path: Path | str,
    *,
    voice: str = DEFAULT_VOICE,
    rate: str = "-4%",
) -> list[WordBoundary]:
    import edge_tts

    output = Path(audio_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(text, voice=voice, rate=rate, boundary="WordBoundary")
    audio_chunks: list[bytes] = []
    words: list[WordBoundary] = []
    async for chunk in communicate.stream():
        chunk_type = chunk.get("type")
        if chunk_type == "audio":
            audio_chunks.append(chunk["data"])
        elif chunk_type == "WordBoundary":
            raw_text = str(chunk.get("text") or "").strip()
            if not raw_text:
                continue
            words.append(
                WordBoundary(
                    text=raw_text,
                    start_ms=_edge_ticks_to_ms(chunk.get("offset", chunk.get("Offset", 0))),
                    duration_ms=_edge_ticks_to_ms(chunk.get("duration", chunk.get("Duration", 0))),
                )
            )
    if not audio_chunks:
        raise RuntimeError("Edge-TTS returned no audio chunks")
    output.write_bytes(b"".join(audio_chunks))
    if not words:
        raise RuntimeError("Edge-TTS returned no WordBoundary data; refusing word-level timing guess")
    return words


def generate_audio_alignment(
    segments: Sequence[dict[str, Any] | NarrationSegment],
    output_dir: Path | str,
    variant_id: str,
    *,
    voice: str = DEFAULT_VOICE,
    rate: str = "-4%",
    silence_threshold_db: int = -38,
) -> AudioAlignment:
    normalized = normalize_segments(segments)
    text = join_segments_for_tts(normalized)
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    audio_path = out / f"{variant_id}_voiceover.mp3"
    words = asyncio.run(synthesize_edge_tts_with_boundaries(text, audio_path, voice=voice, rate=rate))
    trimmed_path, words = trim_tail_silence_if_needed(audio_path, words)
    audio_path = trimmed_path
    duration_ms = probe_media_duration_ms(audio_path)
    silences = detect_audio_silences(audio_path, threshold_db=silence_threshold_db, min_duration_sec=0.08)
    breath_groups = build_breath_groups(normalized, words)
    pauses = confirm_punctuation_pauses(normalized, breath_groups, silences)
    max_internal_silence_ms = max((silence["duration_ms"] for silence in silences if silence["end_ms"] < duration_ms - 250), default=0)
    last_word_end_ms = max((word.end_ms for word in words), default=0)
    alignment = AudioAlignment(
        variant_id=variant_id,
        voice=voice,
        text=text,
        audio_path=str(audio_path),
        duration_ms=duration_ms,
        last_word_end_ms=last_word_end_ms,
        tail_silence_ms=max(0, duration_ms - last_word_end_ms),
        max_internal_silence_ms=max_internal_silence_ms,
        words=words,
        silences=silences,
        pauses=pauses,
        breath_groups=_apply_confirmed_pauses(breath_groups, pauses),
    )
    write_json(out / f"{variant_id}_audio_alignment.json", alignment.to_dict())
    (out / f"{variant_id}_voiceover.txt").write_text(text + "\n", encoding="utf-8")
    return alignment


def build_breath_groups(segments: Sequence[NarrationSegment], words: Sequence[WordBoundary]) -> list[BreathGroup]:
    groups: list[BreathGroup] = []
    cursor = 0
    for segment in segments:
        tokens = WORD_RE.findall(segment.text)
        if not tokens:
            continue
        count = len(tokens)
        segment_words = list(words[cursor : cursor + count])
        if len(segment_words) != count:
            raise RuntimeError(f"WordBoundary/segment mismatch at role {segment.role}")
        groups.append(
            BreathGroup(
                role=segment.role,
                text=segment.text,
                start_ms=segment_words[0].start_ms,
                end_ms=segment_words[-1].end_ms,
                words=segment_words,
            )
        )
        cursor += count
    if cursor != len(words):
        raise RuntimeError(f"unused WordBoundary entries: used={cursor}, total={len(words)}")
    return groups


def confirm_punctuation_pauses(
    segments: Sequence[NarrationSegment],
    groups: Sequence[BreathGroup],
    silences: Sequence[dict[str, int]],
    *,
    min_gap_ms: int = 80,
) -> list[ConfirmedPause]:
    pauses: list[ConfirmedPause] = []
    for index, group in enumerate(groups[:-1]):
        next_group = groups[index + 1]
        segment = segments[index]
        punctuation = bool(PUNCTUATION_RE.search(segment.text.strip()))
        gap_ms = max(0, next_group.start_ms - group.end_ms)
        overlap_ms = _max_silence_overlap(group.end_ms, next_group.start_ms, silences)
        confirmed = punctuation and gap_ms >= min_gap_ms and overlap_ms >= min(60, gap_ms)
        pauses.append(
            ConfirmedPause(
                after_role=group.role,
                start_ms=group.end_ms,
                end_ms=next_group.start_ms,
                duration_ms=gap_ms,
                punctuation=punctuation,
                boundary_gap_ms=gap_ms,
                audio_silence_ms=overlap_ms,
                confirmed=confirmed,
            )
        )
    return pauses


def trim_tail_silence_if_needed(audio_path: Path, words: Sequence[WordBoundary], *, target_tail_ms: int = 260) -> tuple[Path, list[WordBoundary]]:
    duration_ms = probe_media_duration_ms(audio_path)
    last_word_end_ms = max((word.end_ms for word in words), default=duration_ms)
    if duration_ms - last_word_end_ms <= 400:
        return audio_path, list(words)
    trimmed = audio_path.with_name(audio_path.stem + "_trimmed.mp3")
    end_sec = (last_word_end_ms + target_tail_ms) / 1000.0
    command = [
        "ffmpeg",
        "-y",
        "-i",
        str(audio_path),
        "-af",
        f"atrim=0:{end_sec:.3f},asetpts=PTS-STARTPTS",
        "-c:a",
        "libmp3lame",
        "-q:a",
        "4",
        str(trimmed),
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"tail silence trim failed: {completed.stderr[-800:]}")
    return trimmed, list(words)


def detect_audio_silences(audio_path: Path | str, *, threshold_db: int = -38, min_duration_sec: float = 0.08) -> list[dict[str, int]]:
    command = [
        "ffmpeg",
        "-hide_banner",
        "-i",
        str(audio_path),
        "-af",
        f"silencedetect=noise={threshold_db}dB:d={min_duration_sec}",
        "-f",
        "null",
        "-",
    ]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    text = completed.stderr
    starts: list[float] = []
    silences: list[dict[str, int]] = []
    for line in text.splitlines():
        if "silence_start:" in line:
            starts.append(float(line.rsplit("silence_start:", 1)[1].strip().split()[0]))
        elif "silence_end:" in line:
            parts = line.split("silence_end:", 1)[1]
            end = float(parts.split("|", 1)[0].strip())
            duration = float(parts.rsplit("silence_duration:", 1)[1].strip()) if "silence_duration:" in parts else 0.0
            start = starts.pop(0) if starts else max(0.0, end - duration)
            silences.append(
                {
                    "start_ms": int(round(start * 1000)),
                    "end_ms": int(round(end * 1000)),
                    "duration_ms": int(round(duration * 1000)),
                }
            )
    return silences


def probe_media_duration_ms(path: Path | str) -> int:
    command = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=nk=1:nw=1", str(path)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {path}: {completed.stderr[-400:]}")
    return int(round(float(completed.stdout.strip()) * 1000))


def write_json(path: Path | str, payload: dict[str, Any]) -> Path:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_name(output.name + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(output)
    return output


def calculate_elastic_target_duration(
    alignment: dict[str, Any],
    action_floor_ms: int,
    story_floor_ms: int,
    *,
    closure_ms: int = 1200,
    tail_reverb_ms: int = 260,
    legal_min_ms: int = 13000,
    legal_max_ms: int = 24000,
) -> dict[str, Any]:
    """Return the P12S elastic duration target without forcing a 15s edit."""
    tail = max(TAIL_REVERB_MIN_MS, min(TAIL_REVERB_MAX_MS, int(tail_reverb_ms)))
    audio_floor_ms = int(alignment["duration_ms"]) + tail
    natural_target_ms = max(audio_floor_ms, int(action_floor_ms), int(story_floor_ms), int(closure_ms))
    target_ms = min(int(legal_max_ms), max(int(legal_min_ms), natural_target_ms))
    if target_ms <= 16000:
        duration_class = "fast"
    elif target_ms <= 21000:
        duration_class = "standard_narrative"
    else:
        duration_class = "action_showcase"
    return {
        "audio_floor_ms": audio_floor_ms,
        "action_floor_ms": int(action_floor_ms),
        "story_floor_ms": int(story_floor_ms),
        "closure_ms": int(closure_ms),
        "tail_reverb_ms": tail,
        "natural_target_ms": natural_target_ms,
        "target_ms": target_ms,
        "duration_class": duration_class,
        "compressed_for_24s_cap": natural_target_ms > legal_max_ms,
    }


def trim_script_for_24s_cap(segments: Sequence[dict[str, Any]], max_words: int = 58) -> list[dict[str, Any]]:
    """Compact repeated narration before sacrificing action completeness."""
    compacted: list[dict[str, Any]] = []
    seen: set[str] = set()
    for segment in segments:
        words = WORD_RE.findall(str(segment.get("text", "")))
        key = " ".join(word.lower() for word in words[:6])
        if key and key in seen and len(words) > 5:
            continue
        seen.add(key)
        compacted.append(dict(segment))
    while sum(len(WORD_RE.findall(str(item.get("text", "")))) for item in compacted) > max_words and len(compacted) > 3:
        removable = max(range(1, len(compacted) - 1), key=lambda idx: len(WORD_RE.findall(str(compacted[idx].get("text", "")))))
        text_words = WORD_RE.findall(str(compacted[removable].get("text", "")))
        if len(text_words) <= 8:
            break
        compacted[removable]["text"] = " ".join(text_words[:8]) + "."
    return compacted


def _edge_ticks_to_ms(value: Any) -> int:
    return int(round(float(value or 0) / 10000.0))


def _max_silence_overlap(start_ms: int, end_ms: int, silences: Sequence[dict[str, int]]) -> int:
    if end_ms <= start_ms:
        return 0
    best = 0
    for silence in silences:
        overlap = min(end_ms, int(silence["end_ms"])) - max(start_ms, int(silence["start_ms"]))
        best = max(best, overlap)
    return max(0, best)


def _apply_confirmed_pauses(groups: Sequence[BreathGroup], pauses: Sequence[ConfirmedPause]) -> list[BreathGroup]:
    by_role = {pause.after_role: pause for pause in pauses if pause.confirmed}
    updated: list[BreathGroup] = []
    for group in groups:
        pause = by_role.get(group.role)
        updated.append(
            BreathGroup(
                role=group.role,
                text=group.text,
                start_ms=group.start_ms,
                end_ms=group.end_ms + (pause.duration_ms if pause else 0),
                words=group.words,
                punctuation_pause_confirmed_ms=pause.duration_ms if pause else 0,
            )
        )
    return updated
