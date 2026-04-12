"""
Week/Level Pack management for story mode
"""
import json
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

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
    
    def get_chart_names(self):
        """Get list of all available charts"""
        charts = []
        for chart_file in self.charts_path.glob("*.json"):
            try:
                with open(chart_file, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                    charts.append(data.get("name", chart_file.stem))
            except (json.JSONDecodeError, OSError):
                debug_logger.warning("Chart illisible ignore dans la liste: %s", chart_file)
                charts.append(chart_file.stem)
        return sorted(charts)
    
    def get_chart_file(self, chart_name):
        """Get the file name for a chart"""
        # Try exact match first
        if (self.charts_path / f"{chart_name}.json").exists():
            return chart_name
        
        # Try to find by display name
        for chart_file in self.charts_path.glob("*.json"):
            try:
                with open(chart_file, 'r', encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("name") == chart_name:
                        return chart_file.stem
            except (json.JSONDecodeError, OSError):
                pass
        
        return chart_name


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
