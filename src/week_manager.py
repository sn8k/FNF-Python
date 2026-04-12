"""
Week/Level Pack management for story mode
"""
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.chart_compat import ChartEntry, build_chart_display_name, get_chart_key, iter_chart_files, load_chart_file
from src.logging_utils import configure_logging, get_debug_logger, get_user_logger
from src.resources import get_resource_path


user_logger = get_user_logger("week_manager")
debug_logger = get_debug_logger("week_manager")


class Week:
    """Represents a week/level pack"""
    def __init__(self, name, songs=None, enemies=None, background=None):
        self.name = name
        self.songs = songs or []
        self.enemies = enemies or []
        self.background = background
        
    def to_dict(self):
        return {
            "name": self.name,
            "songs": self.songs,
            "enemies": self.enemies,
            "background": self.background
        }
    
    @staticmethod
    def from_dict(data):
        return Week(
            name=data.get("name", ""),
            songs=data.get("songs", []),
            enemies=data.get("enemies", []),
            background=data.get("background")
        )


class WeekManager:
    """Manages weeks/level packs"""
    
    def __init__(self):
        self.weeks_path = get_resource_path("data", "weeks")
        self.weeks_path.mkdir(parents=True, exist_ok=True)
        self.weeks = {}
        self.load_weeks()
    
    def load_weeks(self):
        """Load all weeks from files"""
        self.weeks = {}
        for week_file in self.weeks_path.glob("*.json"):
            try:
                with open(week_file, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                    week = Week.from_dict(data)
                    self.weeks[week.name] = week
            except (json.JSONDecodeError, IOError):
                user_logger.warning("Une week n'a pas pu etre chargee.")
                debug_logger.exception("Echec de chargement de la week %s", week_file)
    
    def save_week(self, week):
        """Save a week to file"""
        week_file = self.weeks_path / f"{week.name}.json"
        with open(week_file, 'w', encoding="utf-8") as f:
            json.dump(week.to_dict(), f, indent=2)
        self.weeks[week.name] = week
        debug_logger.info("Week sauvegardee: %s", week_file)
    
    def delete_week(self, week_name):
        """Delete a week"""
        week_file = self.weeks_path / f"{week_name}.json"
        if week_file.exists():
            week_file.unlink()
        if week_name in self.weeks:
            del self.weeks[week_name]
    
    def get_week_names(self):
        """Get list of all week names"""
        return sorted(self.weeks.keys())
    
    def get_week(self, name):
        """Get a specific week"""
        return self.weeks.get(name)
    
    def create_default_week(self):
        """Create a default story mode week"""
        default_week = Week(
            name="Week 1",
            songs=["test_song"],
            enemies=["test_enemy"],
            background="Sticky.png"
        )
        self.save_week(default_week)


class ChartManager:
    """Manages song charts"""
    
    def __init__(self):
        self.charts_path = get_resource_path("data", "charts")
        self.charts_path.mkdir(parents=True, exist_ok=True)
        self.chart_entries: list[ChartEntry] = []
        self.entries_by_key: dict[str, ChartEntry] = {}
        self.entries_by_display_name: dict[str, ChartEntry] = {}
        self.refresh_library()

    def refresh_library(self):
        """Rebuild the chart discovery index."""
        discovered: list[tuple[ChartEntry, str]] = []
        display_counts: dict[str, int] = {}

        for chart_file in iter_chart_files():
            try:
                normalized_chart = load_chart_file(chart_file)
            except (ValueError, json.JSONDecodeError, OSError):
                debug_logger.warning("Chart illisible ignore dans la liste: %s", chart_file)
                continue

            display_name = build_chart_display_name(normalized_chart, chart_file)
            display_counts[display_name] = display_counts.get(display_name, 0) + 1
            song_name = str(normalized_chart.get("name") or chart_file.stem)
            difficulty = str(normalized_chart.get("_difficulty") or "normal")
            discovered.append(
                (
                    ChartEntry(
                        key=get_chart_key(chart_file),
                        display_name=display_name,
                        path=chart_file,
                        song_name=song_name,
                        difficulty=difficulty,
                    ),
                    display_name,
                )
            )

        self.chart_entries = []
        self.entries_by_key = {}
        self.entries_by_display_name = {}

        for entry, display_name in discovered:
            resolved_display_name = display_name
            if display_counts.get(display_name, 0) > 1:
                resolved_display_name = f"{display_name} ({entry.path.stem})"
            resolved_entry = ChartEntry(
                entry.key,
                resolved_display_name,
                entry.path,
                entry.song_name,
                entry.difficulty,
            )
            self.chart_entries.append(resolved_entry)
            self.entries_by_key[resolved_entry.key] = resolved_entry
            self.entries_by_display_name[resolved_entry.display_name] = resolved_entry

        self.chart_entries.sort(key=lambda entry: entry.display_name.lower())
    
    def get_chart_names(self):
        """Get list of all available charts"""
        self.refresh_library()
        return [entry.display_name for entry in self.chart_entries]

    def get_song_names(self):
        """Get unique song names without splitting visible choices by difficulty."""
        self.refresh_library()
        names_by_folded: dict[str, str] = {}
        for entry in self.chart_entries:
            song_name = entry.song_name or entry.display_name
            names_by_folded.setdefault(song_name.casefold(), song_name)
        return sorted(names_by_folded.values(), key=str.casefold)

    def get_difficulties_for_song(self, song_name):
        """Return available chart entries for a song, sorted easy/normal/hard."""
        self.refresh_library()
        order = {"easy": 0, "normal": 1, "hard": 2}
        folded = str(song_name).casefold()
        entries = [
            entry
            for entry in self.chart_entries
            if (entry.song_name or entry.display_name).casefold() == folded
        ]
        return sorted(entries, key=lambda entry: (order.get(entry.difficulty, 99), entry.display_name.casefold()))
    
    def get_chart_file(self, chart_name):
        """Get the file name for a chart"""
        self.refresh_library()

        if chart_name in self.entries_by_key:
            return chart_name

        entry = self.entries_by_display_name.get(chart_name)
        if entry:
            return entry.key

        normalized_name = str(chart_name).casefold()
        for candidate in self.chart_entries:
            if candidate.display_name.casefold() == normalized_name:
                return candidate.key
            if candidate.path.stem.casefold() == normalized_name:
                return candidate.key

        return chart_name

    def get_chart_path(self, chart_name):
        """Resolve a chart identifier or display name to an on-disk path."""
        chart_key = self.get_chart_file(chart_name)
        entry = self.entries_by_key.get(chart_key)
        if entry:
            return entry.path

        candidate = Path(chart_name)
        if candidate.exists():
            return candidate

        fallback = self.charts_path / f"{chart_name}.json"
        if fallback.exists():
            return fallback
        return None

    def load_chart(self, chart_name):
        """Load a chart by identifier or display name using compatibility rules."""
        chart_path = self.get_chart_path(chart_name)
        if chart_path is None:
            raise FileNotFoundError(f"Chart introuvable: {chart_name}")
        return load_chart_file(chart_path)


def main():
    """CLI smoke entry point for week and chart discovery."""
    configure_logging()
    week_manager = WeekManager()
    chart_manager = ChartManager()

    week_names = week_manager.get_week_names()
    chart_names = chart_manager.get_chart_names()

    if week_names:
        user_logger.info("Weeks disponibles: %s", ", ".join(week_names))
    else:
        user_logger.info("Aucune week disponible dans data/weeks.")

    if chart_names:
        user_logger.info("Charts disponibles: %s", ", ".join(chart_names))
    else:
        user_logger.info("Aucun chart disponible dans data/charts.")


if __name__ == "__main__":
    main()
