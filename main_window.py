import os
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


class MainWindow(QtWidgets.QMainWindow):

    HIDE_WHEN_CLOSE = True

    def __init__(self):
        super().__init__()

        self.in_favourite = False
        self.dst = None
        self.src = None

        self.audio_engine = pyttsx3.init()
        voices = self.audio_engine.getProperty('voices')
        self.audio_engine.setProperty('voice', voices[SETTINGS["audio_voice"]].id)
        self.audio_engine.setProperty('rate', SETTINGS["audio_rate"])

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Translator")
        
        self.ui.originalLangLabel.setText("en")
        self.ui.translatedLangLabel.setText("ru")
        self.ui.swapLabelButton.mouseReleaseEvent = lambda e: self.tt.swap_lang()
        self.ui.listenSrcTextLabelButton.mouseReleaseEvent = lambda e: self.sound_src()
        self.ui.listenDstTextLabelButton.mouseReleaseEvent = lambda e: self.sound_dst()
        self.ui.favouriteLabelButton.mouseReleaseEvent = lambda e: self.favorite_click()
        
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
        self.tt.translate_from_clipboard_hotkey = HOTKEYS.translate_from_clipboard
        self.tt.translate_from_screenshot_hotkey = HOTKEYS.translate_from_screenshot

        self.tt.translation_loading_signal.connect(self.prepare_translation_loading_signal)
        self.tt.translated_signal.connect(self.prepare_translation_signal)
        self.tt.swap_lang_signal.connect(self.swap_lang)
        self.shortcut_swap.activated.connect(lambda: self.tt.swap_lang())
        self.shortcut_sound_src.activated.connect(self.sound_src)
        self.shortcut_sound_dst.activated.connect(self.sound_dst)
        self.shortcut_translate.activated.connect(self.translate)
        self.shortcut_add_to_favorite.activated.connect(self.favorite_click)

    def swap_lang(self, src_lang, dst_lang):
        self.src, self.dst = self.dst, self.src

        self.ui.originalLangLabel.setText(src_lang)
        self.ui.translatedLangLabel.setText(dst_lang)
        self.ui.originalTextField.setPlainText(self.src)
        self.ui.translatedTextField.setPlainText(self.dst)

    def prepare_translation_signal(self, src, dst):
        self.src = src
        self.dst = dst

        self.set_original_text(src)
        self.set_translated_text(dst)
        self.ui.originalTextField.moveCursor(QtGui.QTextCursor.End)

        if len(self.st.get_all_by_word(src)):
            self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_gold_24dp.svg")))
            self.in_favourite = True
        else:
            self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_black_24dp.svg")))
            self.in_favourite = False

    def prepare_translation_loading_signal(self):
        self.set_original_text("Loading...")
        self.set_translated_text("")
        self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_black_24dp.svg")))
        self.in_favourite = False

        self.show()
        self.activateWindow()

    def set_original_text(self, text):
        self.ui.originalTextField.setPlainText(text)

    def set_translated_text(self, text):
        self.ui.translatedTextField.setPlainText(text)

    def favorite_click(self):
        if self.in_favourite:
            self.st.remove(self.src)
            self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_black_24dp.svg")))
        else:
            self.st.append(self.src, self.dst)
            self.ui.favouriteLabelButton.setPixmap(QtGui.QPixmap(os.path.join(ROOT_DIR, "icons/star_rate_gold_24dp.svg")))
        self.in_favourite = not self.in_favourite

    def translate(self):
        self.src = self.ui.originalTextField.toPlainText()
        self.tt.translate(self.src)

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
        
        
