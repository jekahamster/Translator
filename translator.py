import googletrans

from logger_builder import get_logger
from PyQt5 import QtCore

logger = get_logger(__name__)


class Translator(QtCore.QObject):
    translated_signal = QtCore.pyqtSignal(str, str)

    def __init__(self, translator=googletrans.Translator()):
        super().__init__()
        self._translator = translator

    def _translate(self, text, lang_src="en", lang_dst="ru"):
        return self._translator.translate(text, src=lang_src, dest=lang_dst).text

    def translate(self, text, lang_from, lang_to):
        try:
            stripped_text = text.strip()
            translation_result = self._translate(text, lang_from, lang_to).strip()
            self.translated_signal.emit(stripped_text, translation_result)
        except Exception as e:
            self._dst_text = ""
            logger.info(f"Cant translate '{text}'")
            logger.info(e)