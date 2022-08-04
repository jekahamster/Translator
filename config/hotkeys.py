import sys
sys.path.append(".")

import json
import logger_builder

logger = logger_builder.get_logger(__name__)

class HotKeys:
    path = None
    json_data = None

    translate_from_clipboard = None
    translate_from_screenshot = None
    translate_from_text_area = None
    swap_lang = None
    listen_src = None
    listen_dst = None
    add_to_favorite = None
    update = None

    def __init__(self, path, encoding="utf-8"):
        if HotKeys.path != path:
            HotKeys.path = path
            HotKeys.load(path, encoding)

    def __getitem__(self, item):
        return HotKeys.json_data[item]

    @staticmethod
    def load(path, encoding="utf-8"):
        logger.info("Loading hotkeys...")
        with open(path, "r", encoding=encoding) as hotkeys_file:
            data = json.load(hotkeys_file)

        HotKeys.json_data = data
        HotKeys.translate_from_clipboard = data["translate_from_clipboard"]
        HotKeys.translate_from_screenshot = data["translate_from_screenshot"]
        HotKeys.translate_from_text_area = data["translate_from_text_area"]
        HotKeys.swap_lang = data["swap_lang"]
        HotKeys.listen_src = data["listen_src"]
        HotKeys.listen_dst = data["listen_dst"]
        HotKeys.add_to_favorite = data["add_to_favorite"]
        HotKeys.update = data["update"]

        logger.info("Hotkeys was loaded")
        return HotKeys

if __name__ == "__main__":
    pass