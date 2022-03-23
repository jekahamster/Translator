from PyQt5 import QtCore


class StorageThread(QtCore.QThread):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._storage = storage
        self._cursor = storage.cursor()

    def append(self, src, dst):
        self._cursor.execute(f"INSERT INTO words (word, translation) VALUES (?, ?);", (src, dst))
        self._storage.commit()

    def remove(self, src):
        self._cursor.execute(f"DELETE FROM words WHERE word LIKE ?;", (src, ))
        self._storage.commit()

    def get_all_by_word(self, src):
        self._cursor.execute(f"SELECT * FROM words WHERE word LIKE ?;", (src, ))
        return self._cursor.fetchall()

    def terminate(self):
        self._cursor.close()
        super().terminate()

    def run(self):
        pass