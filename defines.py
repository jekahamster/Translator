import os
import pathlib
import logging 

from config.settings import Settings
from config.hotkeys import HotKeys

ROOT_DIR = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))

LANGS_PATH = ROOT_DIR / "config" / "langs.json"
SETTINGS_PATH = ROOT_DIR / "config" / "settings.json"
HOTKEYS_PATH = ROOT_DIR / "config" / "hotkeys.json"
SETTINGS = Settings(SETTINGS_PATH)
HOTKEYS = HotKeys(HOTKEYS_PATH)

DB_PATH = pathlib.Path(SETTINGS.database)

LOG_FILE = ROOT_DIR / "log.log"
LOG_FORMAT = f"%(asctime)s:[%(levelname)s]:%(name)s:(%(filename)s).%(funcName)s(%(lineno)d): %(message)s" 
LOG_DATE_TIME_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL = logging.DEBUG

