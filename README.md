# opensubtitles_downloader
A tool that automatically search and download subtitles for your video files


# Usage
Simple call it from your prompt:
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
