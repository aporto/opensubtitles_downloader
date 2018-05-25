# OpenSubtitles Downloader
This tool automatically downloads the correct subtitle for all your movies.

You simply right-click the folder where your videos are saved, the select "Download subtitles". It will use an internal algorithm to detect the correct subtitle for each video file. If the exact subrtitle is not available, it will download the best available subtitle.

You can also use it to automate the download for several other applications. For example, you can configure your torrent software to automatically download the best subtitle as soon as a torrent arrives.

# Download
1) Download the following zip file:
[https://github.com/aporto/opensubtitles_downloader/archive/master.zip]

# Installing
If you're running on Windows, there is a installer that will set everything for you:
1) Unzip the downloaded file on any folder you want to store the program.
2) Execute the file Windows\installer.exe
3) Follow the instructions on screen:

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

# Automating the torrents
This instruction is for qBittorrent, but will be similar to most of other torrent clients. 

* Open qBittorrent. On the main menu, select Tools -> Options
* The Options window will open. On the left tool bar, select Downloads
* Roll the right scrool bar up to the end, until you see the option "Run external program on torrent completion"
* Check this option
* Under this option, on the text field, type <PATH>\download_subtitle_no_pause.bat "%R"
* Don't forget to keep the quotes aroung %R
* Don't forget to substitute, on the text above, <PATH> to the real path for this file on your computer
* Press Ok to close the options window  
  
![alt text](https://raw.githubusercontent.com/aporto/opensubtitles_downloader/master/images/qbittorrent_options.png)

# Languages id
Check the file config/languages.csv to find out the id for your language

# Planned future improvements
* Create a GUI interface

# Notes
This code is based on [https://github.com/agonzalezro/python-opensubtitles Python OpenSubtitles] library, by [https://github.com/agonzalezro Alexandre Gonzalez]
