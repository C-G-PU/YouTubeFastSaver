import json
import os
from pathlib import Path

SETTINGS_FILE = "settings.json"

DEFAULT_SETTINGS = {
    "theme": "light",
    "download_dir": str(Path.home() / "Downloads"),
    "force_download": False
}

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            # Merge with default settings to ensure all keys exist
            settings = DEFAULT_SETTINGS.copy()
            settings.update(data)
            return settings
    except Exception as e:
        print(f"Error loading settings: {e}")
        return DEFAULT_SETTINGS.copy()

def save_settings(settings):
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print(f"Error saving settings: {e}")
