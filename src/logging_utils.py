"""
Central logging utilities for the project.
"""
from __future__ import annotations

import json
import logging
import shutil
import time
from logging import Handler
from pathlib import Path
from typing import Any

from src.resources import get_resource_path


CONFIG_PATH = get_resource_path("data", "config.json")

DEFAULT_CONFIG: dict[str, Any] = {
    "window": {
        "width": 1280,
        "height": 720,
        "fps": 60,
    },
    "gameplay": {
        "spawn_distance": 500,
        "hit_window": 150,
        "perfect_range": 25,
        "great_range": 50,
        "good_range": 100,
        "bad_range": 150,
        "note_approach_time_ms": 1500,
    },
    "scoring": {
        "perfect": 350,
        "great": 200,
        "good": 100,
        "bad": 0,
        "miss": 0,
    },
    "lanes": 4,
    "note_size": 60,
    "menu": {
        "intro_enabled": True,
        "intro_duration_ms": 2400,
        "title_animation_amplitude_px": 10,
        "title_animation_speed": 0.003,
        "title_rotation_degrees": 2.0,
        "title_scale_amplitude": 0.025,
        "exit_evasion_radius_px": 170,
        "exit_evasion_max_speed_px": 520,
        "exit_evasion_smoothness": 0.18,
    },
    "logging": {
        "directory": "logs",
        "user": {
            "enabled": True,
            "level": "INFO",
            "file": "user.log",
            "console": True,
        },
        "debug": {
            "enabled": True,
            "level": "DEBUG",
            "file": "debug.log",
            "console": False,
        },
    },
}


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = {}
    keys = set(base) | set(override)
    for key in keys:
        base_value = base.get(key)
        override_value = override.get(key)
        if isinstance(base_value, dict) and isinstance(override_value, dict):
            merged[key] = _deep_merge(base_value, override_value)
        elif key in override:
            merged[key] = override_value
        else:
            merged[key] = base_value
    return merged


def _write_json_file(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as config_file:
        json.dump(payload, config_file, indent=2)
        config_file.write("\n")


def load_project_config(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or CONFIG_PATH
    loaded_config: dict[str, Any] = {}
    should_persist = False

    if not path.exists():
        should_persist = True
    else:
        try:
            with open(path, "r", encoding="utf-8") as config_file:
                loaded_config = json.load(config_file)
        except (json.JSONDecodeError, OSError):
            should_persist = True

    merged_config = _deep_merge(DEFAULT_CONFIG, loaded_config)
    if should_persist or merged_config != loaded_config:
        _write_json_file(path, merged_config)

    return merged_config


def _normalize_level(level_name: str, default: int) -> int:
    normalized = getattr(logging, str(level_name).upper(), None)
    if isinstance(normalized, int):
        return normalized
    return default


def _clear_handlers(logger: logging.Logger) -> None:
    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        try:
            handler.close()
        except OSError:
            pass


def _build_handlers(
    logger_config: dict[str, Any],
    log_directory: Path,
    formatter: logging.Formatter,
) -> tuple[list[Handler], int]:
    handlers: list[Handler] = []
    level = _normalize_level(logger_config.get("level", "INFO"), logging.INFO)

    if logger_config.get("console", False):
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        handlers.append(console_handler)

    log_file_name = logger_config.get("file")
    if log_file_name:
        log_directory.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_directory / log_file_name, mode="w", encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    return handlers, level


def _rotated_log_path(log_directory: Path, log_file_name: str, index: int) -> Path:
    path = Path(log_file_name)
    suffix = path.suffix or ".log"
    stem = path.stem if path.suffix else path.name
    return log_directory / f"{stem}.{index}{suffix}"


def rotate_log_file(log_directory: Path, log_file_name: str, keep: int = 3) -> None:
    """Archive the previous startup logs and leave the active log empty."""
    if keep <= 0:
        return

    current_log = log_directory / log_file_name
    if not current_log.exists():
        return

    log_directory.mkdir(parents=True, exist_ok=True)
    oldest_log = _rotated_log_path(log_directory, log_file_name, keep - 1)
    if oldest_log.exists():
        oldest_log.unlink()

    for index in range(keep - 2, -1, -1):
        source = _rotated_log_path(log_directory, log_file_name, index)
        if source.exists():
            _replace_with_retry(source, _rotated_log_path(log_directory, log_file_name, index + 1))

    target = _rotated_log_path(log_directory, log_file_name, 0)
    if not _replace_with_retry(current_log, target):
        try:
            shutil.copy2(current_log, target)
        except OSError:
            pass


def _replace_with_retry(source: Path, target: Path, attempts: int = 5) -> bool:
    for attempt in range(attempts):
        try:
            source.replace(target)
            return True
        except PermissionError:
            if attempt == attempts - 1:
                break
            time.sleep(0.1)
    return False


def rotate_configured_logs(logging_config: dict[str, Any], log_directory: Path) -> None:
    """Rotate all configured project log files once during logging setup."""
    rotated_files: set[str] = set()
    for stream_name in ("user", "debug"):
        logger_config = logging_config.get(stream_name, {})
        log_file_name = logger_config.get("file")
        if not log_file_name or log_file_name in rotated_files:
            continue
        rotate_log_file(log_directory, log_file_name)
        rotated_files.add(log_file_name)


def configure_logging(config_path: Path | None = None) -> dict[str, Any]:
    config = load_project_config(config_path)
    logging_config = config.get("logging", {})
    log_directory = get_resource_path(logging_config.get("directory", "logs"))
    _clear_handlers(logging.getLogger("fnf.user"))
    _clear_handlers(logging.getLogger("fnf.debug"))
    rotate_configured_logs(logging_config, log_directory)

    user_formatter = logging.Formatter("%(asctime)s | USER | %(levelname)s | %(message)s")
    debug_formatter = logging.Formatter(
        "%(asctime)s | DEBUG | %(levelname)s | %(name)s | %(message)s"
    )

    logger_definitions = {
        "fnf.user": (logging_config.get("user", {}), user_formatter),
        "fnf.debug": (logging_config.get("debug", {}), debug_formatter),
    }

    for logger_name, (logger_config, formatter) in logger_definitions.items():
        logger = logging.getLogger(logger_name)
        logger.propagate = False
        _clear_handlers(logger)

        enabled = logger_config.get("enabled", True)
        handlers, level = _build_handlers(logger_config, log_directory, formatter)
        logger.setLevel(level)

        if enabled:
            for handler in handlers:
                logger.addHandler(handler)
        else:
            logger.addHandler(logging.NullHandler())

    return config


def get_user_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(f"fnf.user.{name}")


def get_debug_logger(name: str = "app") -> logging.Logger:
    return logging.getLogger(f"fnf.debug.{name}")
