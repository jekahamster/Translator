from PyQt5 import QtCore


def _create_table_if_not_exist(cursor):
    creation_table_command = """
        CREATE TABLE IF NOT EXISTS favorite (
            `id` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            `original_text` TEXT NOT NULL,
            `translated_text` TEXT NOT NULL,
            `notes` TEXT,
            `lang_from` VARCHAR(255) NOT NULL,
            `lang_to` VARCHAR(255) NOT NULL,
            `date` DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """
    cursor.execute(creation_table_command)


class StorageThread(QtCore.QThread):
    def __init__(self, storage, parent=None):
        super().__init__(parent)
        self._storage = storage
        self._cursor = storage.cursor()
        _create_table_if_not_exist(self._cursor)

    def append(self, src, dst, notes, lang_from, lang_to):
        self._cursor.execute(f"""
                INSERT INTO favorite (original_text, translated_text, notes, lang_from, lang_to) 
                VALUES 
                (?, ?, ?, ?, ?);
            """, (src, dst, notes, lang_from, lang_to))
        self._storage.commit()

    def update(self, src, dst, notes, lang_from, lang_to):
        print(src, dst, notes, lang_from, lang_to)
        self._cursor.execute("""
            UPDATE favorite
            SET 
                translated_text = :dst,
                notes = :notes_
            WHERE
                (original_text LIKE :src) AND (lang_from LIKE :lang_from_) AND (lang_to LIKE :lang_to_)
        """, {"src": src, "dst": dst, "notes_": notes, "lang_from_": lang_from, "lang_to_": lang_to})
        self._storage.commit()

    def remove(self, src, lang_from, lang_to):
        self._cursor.execute("""
                DELETE 
                FROM favorite 
                WHERE (original_text LIKE ?) AND (lang_from LIKE ?) and (lang_to LIKE ?);
            """, (src, lang_from, lang_to))
        self._storage.commit()

    def get_all_by_word(self, src, lang_from, lang_to):
        self._cursor.execute("""
                SELECT * 
                FROM favorite 
                WHERE (original_text LIKE ?) AND (lang_from LIKE ?) AND (lang_to LIKE ?);
            """, (src, lang_from, lang_to))
        all_translation = self._cursor.fetchall()
        columns = [column_description[0] for column_description in self._cursor.description]
        
        result = []
        for translation in all_translation:     # id, original_text, translated_text, ....
            translation_dict = {}
            for index, column in enumerate(columns):
                translation_dict[column] = translation[index]

            result.append(translation_dict)
        
        return result

    def terminate(self):
        self._cursor.close()
        super().terminate()

    def run(self):
        pass