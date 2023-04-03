# Translator

## Description 

This program will help you understand articles, books, and other foreign texts without switching to another tab with a translator, which can cause loss of context and concentration. Simply select the text, press a hotkey, and continue reading. You can also learn new words by adding them to your favorites.

![image](https://user-images.githubusercontent.com/46385682/120347673-2baddf00-c305-11eb-8fc7-584ff733a477.png)

## How to use? 

1) At the first of all, run the main.py. 
2) You can see window with empty fields. The program is added to the system tray. You can close or hide window.

![image](https://user-images.githubusercontent.com/46385682/120344092-f18f0e00-c301-11eb-84d3-b6432a614502.png)

3) Open your document and select or copy text. After that, press the combination specified in the `settings.json` (activation_hotkey)

![image](https://user-images.githubusercontent.com/46385682/120345094-d7a1fb00-c302-11eb-862b-7f2cb0b77b3b.png)

4) For exit, right click on the icon in tray and select *Exit*

![image](https://user-images.githubusercontent.com/46385682/120345615-4e3ef880-c303-11eb-99b2-833b90298e0b.png)

5) Also you can print text on upper text field and press Ctrl+Return (Ctrl+Enter) for translation. For listen text, press on sound icon. For swap languages press on 
incon with thwo arrows between text fiels. And press to start for add word or sentence to favourite 


## Settings

Open `settings.json`

- activation_hotkey - shortcut for activation - string
- database - path to the file that stores the saved words - string 
- audio_rate - audio rate - positive number
- audio_voice - voice type - int number from 0 to 2 
- no_newline - some documents has newline at the end of line, but sentence not finished. Set True for replace all \n\r - boolean 
