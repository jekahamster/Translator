@echo off
cmd /k "cd /d D:\Python\Translator\venv\Scripts & activate & cd /d    D:\Python\Translator & python main.py && exit"


rem https://stackoverflow.com/questions/30927567/a-python-script-that-activates-the-virtualenv-and-then-runs-another-python-scrip
rem CALL "D:\Python\Translator\venv\Scripts\activate.bat"
rem python "D:\Python\Translator\main.py"