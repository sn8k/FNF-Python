"""
Central logging utilities for the project.
"""
from __future__ import annotations

import json
import logging
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


def load_project_config(config_path: Path | None = None) -> dict[str, Any]:
    path = config_path or CONFIG_PATH
    if not path.exists():
        return _deep_merge(DEFAULT_CONFIG, {})

    try:
        with open(path, "r", encoding="utf-8") as config_file:
            loaded_config = json.load(config_file)
    except (json.JSONDecodeError, OSError):
        return _deep_merge(DEFAULT_CONFIG, {})

    return _deep_merge(DEFAULT_CONFIG, loaded_config)


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
        file_handler = logging.FileHandler(log_directory / log_file_name, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

    return handlers, level


def configure_logging(config_path: Path | None = None) -> dict[str, Any]:
    config = load_project_config(config_path)
    logging_config = config.get("logging", {})
    log_directory = get_resource_path(logging_config.get("directory", "logs"))

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
