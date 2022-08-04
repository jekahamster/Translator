import os
import json
import threading 
import sqlite3 
import pyttsx3
import translation_thread
import storage_thread

from defines import ROOT_DIR
from defines import SETTINGS
from defines import HOTKEYS
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

        self.in_favorite = False
        self.dst_text = None
        self.src_text = None

        self.audio_engine = pyttsx3.init()
        voices = self.audio_engine.getProperty('voices')
        self.audio_engine.setProperty('voice', voices[SETTINGS["audio_voice"]].id)
        self.audio_engine.setProperty('rate', SETTINGS["audio_rate"])
        
        self.languages = _load_langs(ROOT_DIR / "config" / "langs.json")

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Translator")
        
        self.ui.originalLangComboBox.addItems(sorted(self.languages.keys()))
        self.ui.translatedLangComboBox.addItems(sorted(self.languages.keys()))
        self.ui.originalLangComboBox.setCurrentText("en")
        self.ui.translatedLangComboBox.setCurrentText("ru")
        self.ui.swapLabelButton.mouseReleaseEvent = lambda e: self.swap_lang()
        self.ui.listenSrcTextLabelButton.mouseReleaseEvent = lambda e: self.sound_src()
        self.ui.listenDstTextLabelButton.mouseReleaseEvent = lambda e: self.sound_dst()
        self.ui.favouriteLabelButton.mouseReleaseEvent = lambda e: self.favorite_click()
        self.ui.originalLangComboBox.currentTextChanged.connect(self.lang_combobox_change)
        self.ui.translatedLangComboBox.currentTextChanged.connect(self.lang_combobox_change)

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ComputerIcon))

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

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.show)
        self.tray_icon.show()
        
        self.database = sqlite3.connect(SETTINGS["database"])
        self.tt = translation_thread.TranslationThread(parent=self)
        self.st = storage_thread.StorageThread(self.database, parent=self)

        self.tt.no_newline = SETTINGS["no_newline"]

        self._set_up_shortcuts()
        self.tt.start()
        self.st.start()

    def _set_up_shortcuts(self):
        self.shortcut_swap = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.swap_lang), self)
        self.shortcut_sound_src = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.listen_src), self)
        self.shortcut_sound_dst = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.listen_dst), self)
        self.shortcut_translate = QtWidgets.QShortcut(self.tr(HOTKEYS.translate_from_text_area), self.ui.originalTextField)
        self.shortcut_add_to_favorite = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.add_to_favorite), self)
        self.shortcut_update = QtWidgets.QShortcut(QtGui.QKeySequence(HOTKEYS.update), self)
        self.tt.translate_from_clipboard_hotkey = HOTKEYS.translate_from_clipboard
        self.tt.translate_from_screenshot_hotkey = HOTKEYS.translate_from_screenshot

        self.tt.translation_loading_signal.connect(self.prepare_translation_loading_signal)
        self.tt.translated_signal.connect(self.prepare_translation_signal)
        # self.tt.swap_lang_signal.connect(self.swap_lang)
        self.shortcut_swap.activated.connect(lambda: self.swap_lang())
        self.shortcut_sound_src.activated.connect(self.sound_src)
        self.shortcut_sound_dst.activated.connect(self.sound_dst)
        self.shortcut_translate.activated.connect(self.translate)
        self.shortcut_add_to_favorite.activated.connect(self.favorite_click)
        self.shortcut_update.activated.connect(self.update_favorite_translation)

    def swap_lang(self):
        # self.src_text, self.dst_text = self.dst_text, self.src_text
        
        self.original_text, self.translated_text = self.translated_text, self.original_text
        self.src_lang, self.dst_lang = self.dst_lang, self.src_lang

    def prepare_translation_signal(self, src, dst):
        self.src_text = src
        self.dst_text = dst

        self.original_text = src
        self.translated_text = dst
        self.ui.originalTextField.moveCursor(QtGui.QTextCursor.End)

    def prepare_translation_loading_signal(self):
        self.original_text = "Loading..."
        self.translated_text = ""
        self.notes = ""
        self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_black_24dp.svg")))
        self.in_favorite = False

        self.show()
        self.activateWindow()

    def favorite_click(self):
        if self.in_favorite:
            self.st.remove(self.src_text, self.src_lang, self.dst_lang)
            self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(str(ROOT_DIR / "icons" / "star_rate_black_24dp.svg")))
        else:
            self.st.append(self.src_text, self.translated_text.strip(), self.notes.strip(), self.src_lang, self.dst_lang)
            self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(str(ROOT_DIR / "icons" / "star_rate_gold_24dp.svg")))
        self.in_favorite = not self.in_favorite

    def lang_combobox_change(self, event):
        self.tt.lang_src = self.src_lang
        self.tt.lang_dst = self.dst_lang
        self.translate()

    def translate(self):
        self.src_text = self.ui.originalTextField.toPlainText().strip()
        self.ui.originalTextField.setPlainText(self.src_text)
        
        saved_translations = self.st.get_all_by_word(self.src_text, self.src_lang, self.dst_lang)

        if len(saved_translations):
            self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_gold_24dp.svg")))
            self.in_favorite = True

            self.dst_text = saved_translations[0]["translated_text"]
            self.translated_text = self.dst_text
            self.notes = saved_translations[0]["notes"]
            return 

        self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_black_24dp.svg")))
        self.in_favorite = False
        self.notes = ""
        self.tt.translate(self.src_text)

    def update_favorite_translation(self):
        if not self.in_favorite:
            return 
        
        original_text = self.original_text.strip()
        translated_text = self.translated_text.strip()
        notes = self.notes.strip()
        lang_from = self.src_lang
        lang_to = self.dst_lang

        self.st.update(original_text, translated_text, notes, lang_from, lang_to)

    def closeEvent(self, event):
        if MainWindow.HIDE_WHEN_CLOSE:
            event.ignore()
            self.hide()

    def hideEvent(self, event):
        event.ignore()
        self.hide()

    def quit(self):
        self.tt.terminate()
        self.st.terminate()
        self.database.close()
        QtWidgets.qApp.quit()

    def sound_src(self):
        threading.Thread(
            target=self.generate_audio, 
            args=(self.ui.originalTextField.toPlainText().strip(), )).start()

    def sound_dst(self):
        threading.Thread(
            target=self.generate_audio, 
            args=(self.ui.translatedTextField.toPlainText().strip(), )).start()

    def generate_audio(self, text):
        self.audio_engine.say(text)
        self.audio_engine.runAndWait()
    
    @property
    def src_lang(self):
        return self.ui.originalLangComboBox.currentText()

    @src_lang.setter
    def src_lang(self, lang):
        self.ui.originalLangComboBox.setCurrentText(lang)
    
    @property
    def dst_lang(self):
        return self.ui.translatedLangComboBox.currentText()

    @dst_lang.setter
    def dst_lang(self, lang):
        return self.ui.translatedLangComboBox.setCurrentText(lang)

    @property
    def original_text(self):
        return self.ui.originalTextField.toPlainText()

    @original_text.setter
    def original_text(self, text):
        self.ui.originalTextField.setPlainText(text)

    @property
    def translated_text(self):
        return self.ui.translatedTextField.toPlainText()

    @translated_text.setter
    def translated_text(self, text):
        self.ui.translatedTextField.setPlainText(text)

    @property
    def notes(self):
        return self.ui.notesField.toPlainText()

    @notes.setter
    def notes(self, text):
        self.ui.notesField.setPlainText(text)