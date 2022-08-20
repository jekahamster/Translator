import os
import json
import threading 
import sqlite3 
import pyttsx3
import translator
import storage
import keyboard_listener

from defines import ROOT_DIR
from defines import SETTINGS
from defines import HOTKEYS
from defines import LANGS_PATH
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from ui_main_window import Ui_MainWindow
from logger_builder import get_logger


logger = get_logger(__name__)


def _load_langs(path):
    langs = None
    with open(path, "r") as file:
        langs = json.load(file)
    return langs


class MainWindow(QtWidgets.QMainWindow):

    HIDE_WHEN_CLOSE = True

    def __init__(self):
        super().__init__()

        self._in_favorite = False
        self._dst_text_cached = None
        self._src_text_cached = None
        self._languages = _load_langs(LANGS_PATH)
        
        self._database = sqlite3.connect(SETTINGS["database"])
        self._translator = translator.Translator()
        self._storage = storage.Storage(self._database)
        self._keyboard_listener = keyboard_listener.KeyboardListener(parent=self)

        self._ui = Ui_MainWindow()
        self._ui.setupUi(self)
        self._setup_ui()
        self._setup_shortcuts()
        
        self._keyboard_listener.start()

    def _setup_ui(self):
        self.setWindowTitle("Translator")

        # audio engine
        self._audio_engine = pyttsx3.init()
        voices = self._audio_engine.getProperty('voices')
        self._audio_engine.setProperty('voice', voices[SETTINGS["audio_voice"]].id)
        self._audio_engine.setProperty('rate', SETTINGS["audio_rate"])

        # set languages dropdown
        self._ui.originalLangComboBox.addItems(sorted(self._languages.keys()))
        self._ui.translatedLangComboBox.addItems(sorted(self._languages.keys()))
        self._ui.originalLangComboBox.setCurrentText("en")
        self._ui.translatedLangComboBox.setCurrentText("ru")
        
        # set tray 
        self._tray_icon = QtWidgets.QSystemTrayIcon(self)
        self._tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))
        show_action = QtWidgets.QAction("Show", self)
        hide_action = QtWidgets.QAction("Hide", self)
        quit_action = QtWidgets.QAction("Exit", self)

        show_action.triggered.connect(self.show)
        hide_action.triggered.connect(self.hide)
        quit_action.triggered.connect(self.quit)

        tray_menu = QtWidgets.QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
        tray_menu.addAction(quit_action)

        self._tray_icon.setContextMenu(tray_menu)
        self._tray_icon.activated.connect(self.show)
        self._tray_icon.show()
        
        # set buttons actions
        self._ui.swapLabelButton.mouseReleaseEvent = lambda e: self.swap_lang()
        self._ui.listenSrcTextLabelButton.mouseReleaseEvent = lambda e: self.sound_src()
        self._ui.listenDstTextLabelButton.mouseReleaseEvent = lambda e: self.sound_dst()
        self._ui.favouriteLabelButton.mouseReleaseEvent = lambda e: self.favorite_click()
        self._ui.originalLangComboBox.currentTextChanged.connect(self.lang_combobox_change)
        self._ui.translatedLangComboBox.currentTextChanged.connect(self.lang_combobox_change)      

    def _setup_shortcuts(self):
        self._shortcut_swap = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.swap_lang), self)
        self._shortcut_sound_src = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.listen_src), self)
        self._shortcut_sound_dst = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.listen_dst), self)
        self._shortcut_translate = QtWidgets.QShortcut(self.tr(HOTKEYS.translate_from_text_area), self._ui.originalTextField)
        self._shortcut_add_to_favorite = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.add_to_favorite), self)
        self._shortcut_update = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.update), self)

        self._keyboard_listener.clipboard_signal.connect(self._prepare_clipboard_signal)
        self._translator.translated_signal.connect(self._prepare_translation_signal)
        self._shortcut_swap.activated.connect(self.swap_lang)
        self._shortcut_sound_src.activated.connect(self.sound_src)
        self._shortcut_sound_dst.activated.connect(self.sound_dst)
        self._shortcut_translate.activated.connect(self.translate_from_ui)
        self._shortcut_add_to_favorite.activated.connect(self.favorite_click)
        self._shortcut_update.activated.connect(self.update_favorite_translation)

    def swap_lang(self):
        # self._src_text_cached, self._dst_text_cached = self._dst_text_cached, self._src_text_cached
        
        self.original_text, self.translated_text = self.translated_text, self.original_text
        self.src_lang, self.dst_lang = self.dst_lang, self.src_lang

    def _prepare_translation_signal(self, src, dst):
        self._src_text_cached = src
        self._dst_text_cached = dst
 
        self.original_text = src
        self.translated_text = dst
        self.notes = ""
        self._ui.originalTextField.moveCursor(QtGui.QTextCursor.End)
        
        self.show()
        self.activateWindow()

    def _prepare_clipboard_signal(self, text):
        self.original_text = text
        self.translate(text)

    def show_loading(self):
        # self.original_text = "Loading..."
        # self.translated_text = ""
        # self.notes = ""

        self.translated_text = "Loading..."
        self.notes = ""

        self._ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_black_24dp.svg")))
        self._in_favorite = False

        self.show()
        self.activateWindow()

    def favorite_click(self):
        if self._in_favorite:
            self._storage.remove(self._src_text_cached, self.src_lang, self.dst_lang)
            self._ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(str(ROOT_DIR / "icons" / "star_rate_black_24dp.svg")))
        else:
            self._storage.append(self._src_text_cached, self.translated_text.strip(), self.notes.strip(), self.src_lang, self.dst_lang)
            self._ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(str(ROOT_DIR / "icons" / "star_rate_gold_24dp.svg")))
        self._in_favorite = not self._in_favorite

    def translate_from_ui(self):
        self._src_text_cached = self._ui.originalTextField.toPlainText().strip()
        self._ui.originalTextField.setPlainText(self._src_text_cached)
        self.translate(self._src_text_cached, self.src_lang, self.dst_lang)

    def translate(self, text=None, lang_from=None, lang_to=None):
        text = text or self.original_text
        lang_from = lang_from or self.src_lang
        lang_to = lang_to or self.dst_lang

        self.show_loading()

        saved_translations = self._storage.get_all_by_word(text, lang_from, lang_to)

        if len(saved_translations):
            self._ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_gold_24dp.svg")))
            self._in_favorite = True

            self._src_text_cached = text
            self._dst_text_cached = saved_translations[0]["translated_text"]

            self.original_text = text                       # for clipboard
            self.translated_text = self._dst_text_cached
            self.notes = saved_translations[0]["notes"]
            return 

        self._ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_black_24dp.svg")))
        self._in_favorite = False
        
        translation_thread = threading.Thread(
            target=self._translator.translate, 
            args=(text, lang_from, lang_to)
        )
        translation_thread.start()

    def update_favorite_translation(self):
        if not self._in_favorite:
            return 
        
        original_text = self.original_text.strip()
        translated_text = self.translated_text.strip()
        notes = self.notes.strip()
        lang_from = self.src_lang
        lang_to = self.dst_lang

        self._storage.update(original_text, translated_text, notes, lang_from, lang_to)

    def closeEvent(self, event):
        if MainWindow.HIDE_WHEN_CLOSE:
            event.ignore()
            self.hide()

    def hideEvent(self, event):
        event.ignore()
        self.hide()

    def lang_combobox_change(self, event):
        self.translate()

    def quit(self):
        self._database.close()
        QtWidgets.qApp.quit()

    def sound_src(self):
        threading.Thread(
            target=self.generate_audio, 
            args=(self._ui.originalTextField.toPlainText().strip(), )).start()

    def sound_dst(self):
        threading.Thread(
            target=self.generate_audio, 
            args=(self._ui.translatedTextField.toPlainText().strip(), )).start()

    def generate_audio(self, text):
        self._audio_engine.say(text)
        self._audio_engine.runAndWait()
    
    @property
    def src_lang(self):
        return self._ui.originalLangComboBox.currentText()

    @src_lang.setter
    def src_lang(self, lang):
        self._ui.originalLangComboBox.setCurrentText(lang)
    
    @property
    def dst_lang(self):
        return self._ui.translatedLangComboBox.currentText()

    @dst_lang.setter
    def dst_lang(self, lang):
        return self._ui.translatedLangComboBox.setCurrentText(lang)

    @property
    def original_text(self):
        return self._ui.originalTextField.toPlainText()

    @original_text.setter
    def original_text(self, text):
        self._ui.originalTextField.setPlainText(text)

    @property
    def translated_text(self):
        return self._ui.translatedTextField.toPlainText()

    @translated_text.setter
    def translated_text(self, text):
        self._ui.translatedTextField.setPlainText(text)

    @property
    def notes(self):
        return self._ui.notesField.toPlainText()

    @notes.setter
    def notes(self, text):
        self._ui.notesField.setPlainText(text)

    @property
    def in_favorite(self):
        return self._in_favorite