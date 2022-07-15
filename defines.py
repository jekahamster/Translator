import os
import pathlib
from config.settings import Settings
from config.hotkeys import HotKeys

ROOT_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

SETTINGS_PATH = ROOT_DIR / "config" / "settings.json"
HOTKEYS_PATH = ROOT_DIR / "config" / "hotkeys.json"
SETTINGS = Settings(SETTINGS_PATH)
HOTKEYS = HotKeys(HOTKEYS_PATH)

DB_PATH = pathlib.Path(SETTINGS.database)