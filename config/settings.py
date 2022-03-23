import sys
sys.path.append(".")

import json
import logger_builder

logger = logger_builder.get_logger(__name__)

class Settings:
    path = None
    json_data = None

    database = None
    audio_rate = None
    audio_voice = None
    no_newline = None

    def __init__(self, path, encoding="utf-8"):
        if Settings.path != path:
            Settings.path = path
            Settings.load(path, encoding)

    def __getitem__(self, item):
        return Settings.json_data[item]

    @staticmethod
    def load(path, encoding="utf-8"):
        logger.info("Loading settings...")

        with open(path, "r", encoding=encoding) as settings_file:
            data = json.load(settings_file)

        Settings.json_data = data
        Settings.database = data["database"]
        Settings.audio_rate = int(data["audio_rate"])
        Settings.audio_voice = int(data["audio_voice"])
        Settings.no_newline = bool(data["no_newline"])
        
        logger.info("Settings was loaded")

        return Settings


if __name__ == "__main__":
    pass