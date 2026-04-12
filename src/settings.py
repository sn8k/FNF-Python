"""
Settings management for FNF - handles saving/loading game settings
"""
from copy import deepcopy
import json
from src.logging_utils import get_debug_logger, get_user_logger
from src.resources import get_resource_path


user_logger = get_user_logger("settings")
debug_logger = get_debug_logger("settings")

class Settings:
    """Manages game settings and preferences"""
    
    DEFAULT_SETTINGS = {
        "keybinds": {
            "left": "a",
            "down": "s",
            "up": "w",
            "right": "d",
        },
        "note_colors": {
            "left": [255, 0, 0],      # Red
            "down": [0, 255, 0],      # Green
            "up": [0, 0, 255],        # Blue
            "right": [255, 255, 0],   # Yellow
        },
        "scroll_mode": "downscroll",  # downscroll, upscroll, sidescroll
        "volume": {
            "master": 70,
            "music": 70,
            "effects": 70,
        }
    }
    
    def __init__(self):
        self.settings_path = get_resource_path("data", "settings.json")
        self.settings = deepcopy(self.DEFAULT_SETTINGS)
        self.load_settings()
        
    def load_settings(self):
        """Load settings from file"""
        if self.settings_path.exists():
            try:
                with open(self.settings_path, 'r', encoding="utf-8") as f:
                    saved = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    self.settings = {**deepcopy(self.DEFAULT_SETTINGS), **saved}
            except (json.JSONDecodeError, IOError):
                user_logger.warning("Parametres invalides, chargement des valeurs par defaut.")
                debug_logger.exception(
                    "Echec du chargement des parametres depuis %s", self.settings_path
                )
        else:
            self.save_settings()
    
    def save_settings(self):
        """Save settings to file"""
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.settings_path, 'w', encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2)
        debug_logger.debug("Parametres sauvegardes dans %s", self.settings_path)
    
    def get(self, key, default=None):
        """Get a setting value"""
        keys = key.split('.')
        value = self.settings
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k, default)
            else:
                return default
        return value if value is not None else default
    
    def set(self, key, value):
        """Set a setting value"""
        keys = key.split('.')
        var = self.settings
        for k in keys[:-1]:
            if k not in var:
                var[k] = {}
            var = var[k]
        var[keys[-1]] = value
        self.save_settings()
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = deepcopy(self.DEFAULT_SETTINGS)
        self.save_settings()
