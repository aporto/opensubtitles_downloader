# opensubtitles_downloader
A tool that automatically search and download subtitles for your video files

# Installing
If you're running on Windows, there is a installer that will set everything for you:
1) Download the zip file: [https://github.com/aporto/opensubtitles_downloader/archive/master.zip]
2) Unzip it on any folder you want to store the program.
3) Execute the file Windows\installer.exe
4) Follow the instructions on screen:

The installer will ask for username and password for OpenSubtitles.org. If you don't have this information, go to the website and register
![alt text](https://github.com/aporto/opensubtitles_downloader/blob/master/images/login_check.png)

The installer will show this message, informing that it needs permission to configure Windows to add a context-menu to Windows Explorer
![alt text](https://github.com/aporto/opensubtitles_downloader/blob/master/images/registry_editor.png)


# Usage (simplified)
Using Windows Exploer, right click the folder where your video files are stored. If the installation was correct, you should see the option "Download subtitles":
![alt text](https://github.com/aporto/opensubtitles_downloader/blob/master/images/context_menu.png)

When you select the option "Download subtitles", you shall see this window, showing the search/download progress:
![alt text](https://github.com/aporto/opensubtitles_downloader/blob/master/images/download.png)

When the download is finished, check your video folder. You will find all subtitles (That the program found) already renamed with the same video file name

# Usage (advanced)
If you're not afraid of command-line programs, simple call it from your prompt:
```
python osd.py <USERNAME> <PASSWORD> <MOVIES-FOLDER> <LANGUAGE-ID> [ALTERNATE-LANGUAGE-ID]...
```
  
* <USERNAME> and <PASSWORD> are mandatory for OpenSubtitles.org. If you don't have it, register on the web site
* <MOVIES-FOLDER> The full-path for the path where your movie/series files are stored. The script will search recursivelly
* <LANGUAGE-ID> Provides one or more language-ids, separated by space. The first one will get the highest priority
  
Example:
```
python osd.py jose 123456 c:\movies pob eng
```
This will search subtitles for every file found on c:\movies. It will try to find a Brazilian-Portuguese subtitle. If no one is found, it will search for an English version

# Languages id
Check the file config/languages.csv to find out the id for your language

# Dependencies
This script requires 7-zip. You must have it installed on your computer. If you're not running this on Windows, you change change the code to work with your preferred zip extractor. 

# Planned future improvements
* Create a GUI interface
* Embed a Python zip library, to remove  the dependency on 7-zip installation

# Notes
This code is based on [https://github.com/agonzalezro/python-opensubtitles Python OpenSubtitles] library, by [https://github.com/agonzalezro Alexandre Gonzalez]
