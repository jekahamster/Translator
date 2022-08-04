import time
import os
import keyboard
import pyperclip
import pyautogui
import translator

from defines import ROOT_DIR
from config.settings import Settings
from PyQt5 import QtCore
from logger_builder import get_logger
# from pynput import keyboard

logger = get_logger(__name__)

SETTINGS = Settings(os.path.join(ROOT_DIR, "config/settings.json"))

class TranslationThread(QtCore.QThread):
    translation_loading_signal = QtCore.pyqtSignal()
    translated_signal = QtCore.pyqtSignal(str, str)
    swap_lang_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._translate_from_clipboard_hotkey = None
        self._translate_from_screenshot_hotkey = None
        self._translator = translator.Translator()
        self._no_newline = False

        self._src_text = ""
        self._dst_text = ""

        self._lang_src = "en"
        self._lang_dst = "ru"

    def run(self):
        try:
            if self._translate_from_clipboard_hotkey is not None:
                keyboard.add_hotkey(self._translate_from_clipboard_hotkey, self.translate_from_clipboard)
            
            if self._translate_from_screenshot_hotkey is not None:
                keyboard.add_hotkey(self._translate_from_screenshot_hotkey, self.translate_from_screenshot)
        except ValueError as ve:
            logger.exception(f"Invalid hotkey for this layout")
            exit()

        keyboard.wait()

    def translate_from_screenshot(self):
        try:
            text = self._get_text_from_screenshot()
            self._src_text = text
            self._dst_text = self._translte(text)
            self.translated_signal.emit(self._src_tex, self._dst_text)
        except Exception as e:
            self._dst_text = ""
            logger.info(f"Cant translate from screenshot")
            logger.info(e)

    def _get_text_from_screenshot(self):
        screenshot = pyautogui.screenshot()
        print(screenshot)

    def translate_from_clipboard(self): 
        try:
            text = self._get_clipboard_data()
            self.translation_loading_signal.emit()
            self._src_text = text.strip()
            self._dst_text = self._translate(text).strip()

            self.translated_signal.emit(self._src_text, self._dst_text)
        except TypeError as e:
            logger.info(f"\nCant translate from clipboard\n{e}")
            self._dst_text = ""
            self._src_text = ""
            self.translated_signal.emit(self._src_text, self._dst_text)
        except Exception as e:
            self._dst_text = ""
            logger.info(f"\nCant translate from clipboard\n{e}")

    def translate(self, text, src_lang=None, dst_lang=None):
        if src_lang and dst_lang:
            self._lang_src = src_lang
            self._lang_dst = dst_lang
            
        try:
            self._src_text = text.strip()
            self._dst_text = self._translate(text).strip()
            self.translated_signal.emit(self._src_text, self._dst_text)
        except Exception as e:
            self._dst_text = ""
            logger.info(f"Cant translate '{text}'")
            logger.info(e)

    def _get_clipboard_data(self):
        prev_data = pyperclip.paste()
        pyautogui.hotkey('ctrl', 'c')
        time.sleep(SETTINGS.waiting_for_copy)
        text = pyperclip.paste().strip()
        pyperclip.copy(prev_data)

        if self._no_newline:
            text = text.replace("\n", " ").replace("\r", "")
        
        return text

    def _translate(self, text):
        return self._translator.translate(text, self._lang_src, self._lang_dst)
        

    def swap_lang(self):
        self._lang_src, self._lang_dst = self._lang_dst, self._lang_src
        self._src_text, self._dst_text = self._dst_text, self._src_text

        # self.swap_lang_signal.emit(self._lang_src, self._lang_dst)

    @property
    def lang_src(self):
        return self._lang_src

    @property
    def lang_dst(self):
        return self._lang_dst

    @property
    def translate_from_clipboard_hotkey(self):
        return self._translate_from_clipboard_hotkey
    
    @property
    def translate_from_screenshot_hotkey(self):
        return self._translate_from_screenshot_hotkey

    @property 
    def no_newline(self):
        return self._no_newline

    @translate_from_clipboard_hotkey.setter
    def translate_from_clipboard_hotkey(self, hotkey):
        self._translate_from_clipboard_hotkey = hotkey

    @translate_from_screenshot_hotkey.setter
    def translate_from_screenshot_hotkey(self, hotkey):
        self._translate_from_screenshot_hotkey = hotkey

    @no_newline.setter
    def no_newline(self, value):
        self._no_newline = value

    @lang_src.setter
    def lang_src(self, lang):
        self._lang_src = lang

    @lang_dst.setter
    def lang_dst(self, lang):
        self._lang_dst = lang

        
