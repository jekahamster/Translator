import sys
import pathlib 
import argparse
import sqlite3


MAX_WORDS_COUNT = 5


def convert(lang_from, lang_to, db_path, output_path, reverse=False):
    database = sqlite3.connect(str(db_path))
    cursor = database.cursor()

    cursor.execute("""
        SELECT original_text, translated_text, notes 
        FROM favorite
        WHERE lang_from = :lang_from_ AND lang_to = :lang_to_;
    """, {"lang_from_": lang_from, "lang_to_": lang_to})

    result = cursor.fetchall()
    
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(";\n")
        
        for word, translation, notes in result:
            if len(word.split()) > MAX_WORDS_COUNT:
                continue

            word = word.replace("\"", "\"\"")
            translation = translation.replace("\"", "\"\"")
            notes = notes.replace("\"", "\"\"")

            front_card = None
            back_card = None

            if not reverse:
                front_card = f'"{word}"'
                if notes:
                    back_card = f'"{translation}\n\nNotes:\n{notes}"'
                else:
                    back_card = f'"{translation}"'
            else:
                front_card = f'"{translation}"'
                if notes:
                    back_card = f'"{word}\n\nNotes:\n{notes}"'
                else:
                    back_card = f'"{word}"'
            
            file.write(f"{front_card};{back_card}\n")



def build_parser():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "-p", "--path",
        action="store",
        default="../database/translator.db",
        dest="path"
    )

    parser.add_argument(
        "-r", "--reverse",
        action="store_true",
        dest="reverse"
    )

    parser.add_argument(
        "-f", "--lang-from",
        action="store",
        default="en",
        dest="lang_from"
    )

    parser.add_argument(
        "-t", "--lang-to",
        action="store",
        default="ru",
        dest="lang_to"
    )

    parser.add_argument(
        "-o", "--output",
        action="store",
        default="./words.txt",
        dest="output"
    )

    return parser

def main(args):
    parser = build_parser()
    parsing_results = parser.parse_args(args)
    
    convert(
        lang_from=parsing_results.lang_from,
        lang_to=parsing_results.lang_to,
        db_path=parsing_results.path,
        output_path=parsing_results.output,
        reverse=parsing_results.reverse 
    )
    

if __name__ == "__main__":
    main(sys.argv[1:])