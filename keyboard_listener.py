import time 
import pyautogui
import keyboard
import pyperclip

from defines import SETTINGS
from defines import HOTKEYS
from logger_builder import get_logger
from PyQt5 import QtCore


logger = get_logger(__name__)


class KeyboardListener(QtCore.QThread):
    clipboard_signal = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

    def run(self):
        try:
            if HOTKEYS.translate_from_clipboard:
                keyboard.add_hotkey(HOTKEYS.translate_from_clipboard, self._send_clipboard_data)

            if HOTKEYS.translate_from_screenshot:
                keyboard.add_hotkey(HOTKEYS.translate_from_screenshot, self._send_screenshot_data)
        except ValueError as ve:
            logger.exception(f"Invalid hotkey for this layout")
            exit()

        keyboard.wait()
    
    def _send_clipboard_data(self):
        clipboard_data = self._get_clipboard_data()
        self.clipboard_signal.emit(clipboard_data)

    def _send_screenshot_data(self):
        raise NotImplementedError
    
    def _get_clipboard_data(self):
        prev_data = pyperclip.paste()
        pyautogui.hotkey('ctrl', 'c')
        
        time.sleep(SETTINGS.waiting_for_copy)
        
        text = pyperclip.paste().strip()
        pyperclip.copy(prev_data)

        if SETTINGS.no_newline:
            text = text.replace("\n", " ").replace("\r", "")
        
        return text

    def _get_text_from_screenshot(self):
        screenshot = pyautogui.screenshot()
        raise NotImplementedError
