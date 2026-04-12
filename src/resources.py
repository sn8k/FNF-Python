"""
Resource path helpers for runtime and packaged executable builds.
"""
import sys
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root path.

    When the application is bundled with PyInstaller, sys.frozen is True and
    sys._MEIPASS points to the temporary extraction folder. Otherwise, the root
    directory is the parent of the src package.
    """
    if getattr(sys, "frozen", False):
        return Path(sys._MEIPASS).resolve()
    return Path(__file__).resolve().parent.parent


def get_resource_path(*path_segments: str) -> Path:
    """Return an absolute resource path for the given relative segments."""
    return get_project_root().joinpath(*path_segments)
