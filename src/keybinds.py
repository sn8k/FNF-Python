"""
Keybind helpers shared by runtime and menu screens.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any

import pygame


LANE_ACTIONS = ("left", "down", "up", "right")

LEGACY_PHYSICAL_KEYS = {
    "q": ("q", pygame.KSCAN_A),
    "z": ("z", pygame.KSCAN_W),
    "a": ("a", pygame.KSCAN_A),
    "s": ("s", pygame.KSCAN_S),
    "w": ("w", pygame.KSCAN_W),
    "d": ("d", pygame.KSCAN_D),
    "left": ("left", getattr(pygame, "KSCAN_LEFT", None)),
    "down": ("down", getattr(pygame, "KSCAN_DOWN", None)),
    "up": ("up", getattr(pygame, "KSCAN_UP", None)),
    "right": ("right", getattr(pygame, "KSCAN_RIGHT", None)),
}

DEFAULT_BINDINGS = {
    "left": {"key": "a", "scancode": pygame.KSCAN_A, "display": "A"},
    "down": {"key": "s", "scancode": pygame.KSCAN_S, "display": "S"},
    "up": {"key": "w", "scancode": pygame.KSCAN_W, "display": "W"},
    "right": {"key": "d", "scancode": pygame.KSCAN_D, "display": "D"},
}


def clone_keybind(binding: Any) -> dict[str, Any] | None:
    """Return a detached keybind copy."""
    if not isinstance(binding, dict):
        return None
    return deepcopy(binding)


def default_keybind(action: str) -> dict[str, Any]:
    """Return the default binding for one lane action."""
    return deepcopy(DEFAULT_BINDINGS.get(action, {"key": "", "scancode": None, "display": "UNBOUND"}))


def _coerce_key_name(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text.lower() or None


def _display_from_key_name(key_name: str | None) -> str:
    if not key_name:
        return "UNBOUND"
    return key_name.upper()


def _key_code_from_name(key_name: str | None) -> int | None:
    if not key_name:
        return None
    try:
        return pygame.key.key_code(key_name)
    except (ValueError, TypeError):
        return None


def _normalize_from_legacy_string(raw_binding: Any) -> dict[str, Any] | None:
    key_name = _coerce_key_name(raw_binding)
    if not key_name:
        return None

    legacy = LEGACY_PHYSICAL_KEYS.get(key_name)
    if legacy is not None:
        key_name, scancode = legacy
    else:
        scancode = None

    return {
        "key": key_name,
        "scancode": scancode,
        "display": _display_from_key_name(key_name),
    }


def normalize_keybind(action: str, raw_binding: Any) -> dict[str, Any]:
    """Normalize a persisted or captured keybind into the project schema."""
    if isinstance(raw_binding, dict):
        key_name = _coerce_key_name(raw_binding.get("key"))
        scancode = raw_binding.get("scancode")
        try:
            scancode = int(scancode) if scancode is not None else None
        except (TypeError, ValueError):
            scancode = None
        display = str(raw_binding.get("display") or "").strip() or _display_from_key_name(key_name)
        if key_name or scancode is not None:
            return {
                "key": key_name,
                "scancode": scancode,
                "display": display,
            }

    normalized = _normalize_from_legacy_string(raw_binding)
    if normalized is not None:
        return normalized

    return default_keybind(action)


def normalize_keybinds(raw_keybinds: Any) -> dict[str, dict[str, Any]]:
    """Normalize the whole lane mapping and fill missing actions."""
    source = raw_keybinds if isinstance(raw_keybinds, dict) else {}
    return {action: normalize_keybind(action, source.get(action)) for action in LANE_ACTIONS}


def build_keybind_from_event(event: pygame.event.Event) -> dict[str, Any]:
    """Create a persisted keybind from a pygame KEYDOWN event."""
    key_name = pygame.key.name(event.key)
    return {
        "key": _coerce_key_name(key_name),
        "scancode": getattr(event, "scancode", None),
        "display": _display_from_key_name(key_name),
    }


def binding_label(binding: Any) -> str:
    """Return the short user-facing label for one binding."""
    normalized = normalize_keybind("", binding)
    return str(normalized.get("display") or "UNBOUND")


def bindings_conflict(left: Any, right: Any) -> bool:
    """Return True when two bindings map to the same physical or logical key."""
    left_binding = normalize_keybind("", left)
    right_binding = normalize_keybind("", right)

    left_scancode = left_binding.get("scancode")
    right_scancode = right_binding.get("scancode")
    if left_scancode is not None and right_scancode is not None:
        return left_scancode == right_scancode

    left_key = _key_code_from_name(left_binding.get("key"))
    right_key = _key_code_from_name(right_binding.get("key"))
    if left_key is None or right_key is None:
        return False
    return left_key == right_key


def binding_matches_event(binding: Any, event: pygame.event.Event) -> bool:
    """Return True when a pygame keyboard event matches the saved binding."""
    normalized = normalize_keybind("", binding)
    event_scancode = getattr(event, "scancode", None)
    binding_scancode = normalized.get("scancode")
    if binding_scancode is not None and event_scancode is not None:
        return binding_scancode == event_scancode

    key_code = _key_code_from_name(normalized.get("key"))
    if key_code is None:
        return False
    return getattr(event, "key", None) == key_code
