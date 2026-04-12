"""
Chart compatibility helpers for native project charts and FNF-style test data.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.resources import get_project_root, get_resource_path


IGNORED_CHART_FILENAMES = {"events.json", "preload.json"}
DIFFICULTY_SUFFIXES = ("easy", "normal", "hard")


@dataclass(frozen=True)
class ChartEntry:
    """Resolved chart entry available to the runtime and editors."""

    key: str
    display_name: str
    path: Path


def get_chart_roots() -> list[Path]:
    """Return the directories scanned for chart files."""
    return [
        get_resource_path("data", "charts"),
        get_resource_path("test-data", "charts"),
    ]


def iter_chart_files() -> list[Path]:
    """Return all supported chart files from known roots."""
    chart_files: list[Path] = []

    for root in get_chart_roots():
        if not root.exists():
            continue
        for chart_path in sorted(root.rglob("*.json")):
            if chart_path.name in IGNORED_CHART_FILENAMES:
                continue
            chart_files.append(chart_path)

    return chart_files


def get_chart_key(chart_path: Path) -> str:
    """Return a stable project-relative identifier for a chart path."""
    resolved = chart_path.resolve()
    try:
        return resolved.relative_to(get_project_root()).as_posix()
    except ValueError:
        return resolved.as_posix()


def read_chart_file(chart_path: Path) -> Any:
    """Load raw JSON from a chart file."""
    with open(chart_path, "r", encoding="utf-8") as chart_file:
        return json.load(chart_file)


def load_chart_file(chart_path: Path) -> dict[str, Any]:
    """Load and normalize a chart file from disk."""
    return normalize_chart_data(read_chart_file(chart_path), source_path=chart_path)


def normalize_chart_data(raw_chart: Any, source_path: Path | None = None) -> dict[str, Any]:
    """Normalize native or FNF-style chart JSON into the project schema."""
    if not isinstance(raw_chart, dict):
        raise ValueError("Le chart doit etre un objet JSON.")

    if _is_native_chart(raw_chart):
        return _normalize_native_chart(raw_chart, source_path)

    wrapped_song = raw_chart.get("song")
    if isinstance(wrapped_song, dict):
        return _normalize_sectioned_chart(wrapped_song, source_path)

    if isinstance(raw_chart.get("notes"), list) and any(
        key in raw_chart for key in ("song", "player1", "player2", "bpm", "speed", "needsVoices")
    ):
        return _normalize_sectioned_chart(raw_chart, source_path)

    raise ValueError("Format de chart non supporte.")


def build_chart_display_name(chart: dict[str, Any], source_path: Path | None = None) -> str:
    """Build a user-facing chart name with difficulty when available."""
    base_name = str(chart.get("name") or _infer_chart_name(None, source_path))
    difficulty = chart.get("_difficulty")

    if difficulty:
        return f"{base_name} [{difficulty}]"
    return base_name


def serialize_chart(chart: dict[str, Any]) -> dict[str, Any]:
    """Return the project-native flat chart schema ready for writing."""
    serialized: dict[str, Any] = {
        "name": str(chart.get("name") or "New Song"),
        "bpm": _coerce_number(chart.get("bpm"), 120),
        "offset": _coerce_int(chart.get("offset"), 0),
        "notes": [],
    }

    audio_reference = chart.get("audio")
    if audio_reference:
        serialized["audio"] = _normalize_relative_path(audio_reference)

    for key in ("player", "enemy"):
        character_name = chart.get(key)
        if isinstance(character_name, str) and character_name.strip():
            serialized[key] = character_name.strip()

    for note in chart.get("notes", []):
        if not isinstance(note, dict):
            continue

        try:
            time_ms = _coerce_int(note.get("time"), 0)
            lane = int(note.get("lane", 0))
        except (TypeError, ValueError):
            continue

        serialized_note: dict[str, Any] = {
            "time": time_ms,
            "lane": lane,
        }
        hold_length = _coerce_int(note.get("hold"), 0)
        if hold_length > 0:
            serialized_note["hold"] = hold_length
        serialized["notes"].append(serialized_note)

    serialized["notes"].sort(key=lambda note: (note["time"], note["lane"]))
    return serialized


def get_default_export_path(chart_path: Path, chart: dict[str, Any]) -> Path:
    """Choose a safe save target for imported charts."""
    native_root = get_resource_path("data", "charts")
    resolved = chart_path.resolve()

    try:
        resolved.relative_to(native_root.resolve())
        return chart_path
    except ValueError:
        export_name = _slugify_export_name(chart.get("name") or chart_path.stem)
        return native_root / f"{export_name}.json"


def _is_native_chart(chart: dict[str, Any]) -> bool:
    notes = chart.get("notes")
    if not isinstance(notes, list):
        return False

    first_note = next((note for note in notes if note is not None), None)
    if first_note is None:
        return all(key in chart for key in ("name", "bpm", "offset"))

    return isinstance(first_note, dict) and "time" in first_note and "lane" in first_note


def _normalize_native_chart(chart: dict[str, Any], source_path: Path | None) -> dict[str, Any]:
    normalized = serialize_chart(chart)
    normalized["name"] = str(chart.get("name") or _infer_chart_name(chart.get("name"), source_path))
    normalized["audio"] = chart.get("audio") or _infer_chart_audio(source_path)
    for key in ("player", "enemy"):
        if isinstance(chart.get(key), str) and chart.get(key).strip():
            normalized[key] = chart[key].strip()
    normalized["_source_format"] = "native"
    if source_path is not None:
        normalized["_source_path"] = get_chart_key(source_path)
        normalized["_difficulty"] = _detect_difficulty(source_path)
    return normalized


def _normalize_sectioned_chart(song_data: dict[str, Any], source_path: Path | None) -> dict[str, Any]:
    chart_name = _infer_chart_name(song_data.get("song"), source_path)
    normalized_notes: list[dict[str, Any]] = []
    ignored_opponent_notes = 0

    for section in song_data.get("notes", []):
        if not isinstance(section, dict):
            continue

        must_hit_section = bool(section.get("mustHitSection", False))
        for raw_note in section.get("sectionNotes", []):
            if not isinstance(raw_note, (list, tuple)) or len(raw_note) < 2:
                continue

            try:
                raw_lane = int(raw_note[1])
            except (TypeError, ValueError):
                continue

            is_player_note = must_hit_section
            if raw_lane >= 4:
                is_player_note = not is_player_note

            if not is_player_note:
                ignored_opponent_notes += 1
                continue

            note: dict[str, Any] = {
                "time": _coerce_int(raw_note[0], 0),
                "lane": raw_lane % 4,
            }
            if len(raw_note) >= 3:
                hold_length = _coerce_int(raw_note[2], 0)
                if hold_length > 0:
                    note["hold"] = hold_length
            normalized_notes.append(note)

    normalized_notes.sort(key=lambda note: (note["time"], note["lane"]))

    normalized: dict[str, Any] = {
        "name": chart_name,
        "bpm": _coerce_number(song_data.get("bpm"), 120),
        "offset": 0,
        "notes": normalized_notes,
        "audio": _normalize_relative_path(song_data.get("audio")) or _infer_chart_audio(source_path),
        "_source_format": "fnf_sectioned",
        "_ignored_opponent_notes": ignored_opponent_notes,
        "_difficulty": _detect_difficulty(source_path),
    }

    metadata = {
        key: value
        for key, value in (
            ("player1", song_data.get("player1")),
            ("player2", song_data.get("player2")),
            ("gfVersion", song_data.get("gfVersion")),
            ("speed", song_data.get("speed")),
            ("needsVoices", song_data.get("needsVoices")),
        )
        if value is not None
    }
    if metadata:
        normalized["metadata"] = metadata

    if source_path is not None:
        normalized["_source_path"] = get_chart_key(source_path)

    return normalized


def _infer_chart_name(raw_name: Any, source_path: Path | None) -> str:
    if isinstance(raw_name, str) and raw_name.strip():
        return raw_name.strip()

    fallback = "New Song"
    if source_path is None:
        return fallback

    stem = _strip_difficulty_suffix(source_path.stem)
    if source_path.parent.name.lower() == stem.lower():
        stem = source_path.parent.name
    display = stem.replace("_", " ").replace("-", " ").strip()
    return display.title() if display else fallback


def _detect_difficulty(source_path: Path | None) -> str | None:
    if source_path is None:
        return None

    lower_stem = source_path.stem.lower()
    for difficulty in DIFFICULTY_SUFFIXES:
        if lower_stem.endswith(f"-{difficulty}"):
            return difficulty
    return None


def _strip_difficulty_suffix(stem: str) -> str:
    lower_stem = stem.lower()
    for difficulty in DIFFICULTY_SUFFIXES:
        suffix = f"-{difficulty}"
        if lower_stem.endswith(suffix):
            return stem[: -len(suffix)]
    return stem


def _infer_chart_audio(source_path: Path | None) -> str | None:
    if source_path is None:
        return None

    test_chart_root = get_resource_path("test-data", "charts")
    test_music_root = get_resource_path("test-data", "music")
    try:
        relative_chart_path = source_path.resolve().relative_to(test_chart_root.resolve())
    except ValueError:
        return None

    if not relative_chart_path.parts:
        return None

    song_folder = relative_chart_path.parts[0]
    for candidate_name in ("Inst.ogg", "Inst.mp3", "Inst.wav"):
        candidate = test_music_root / song_folder / candidate_name
        if candidate.exists():
            return get_chart_key(candidate)
    return None


def _coerce_number(value: Any, default: float | int) -> float | int:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        numeric = float(default)

    if numeric.is_integer():
        return int(numeric)
    return numeric


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(round(float(value)))
    except (TypeError, ValueError):
        return default


def _normalize_relative_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None

    return Path(value.strip()).as_posix()


def _slugify_export_name(value: Any) -> str:
    raw = str(value or "imported_chart").strip().lower()
    characters = []
    previous_was_separator = False

    for char in raw:
        if char.isalnum():
            characters.append(char)
            previous_was_separator = False
        elif not previous_was_separator:
            characters.append("_")
            previous_was_separator = True

    slug = "".join(characters).strip("_")
    return slug or "imported_chart"
