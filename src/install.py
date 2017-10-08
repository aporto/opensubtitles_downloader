#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      alex
#
# Created:     06/10/2017
# Copyright:   (c) alex 2017
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import os, sys

from config import config as config
from pythonopensubtitles.opensubtitles import OpenSubtitles
import pythonopensubtitles.utils as osu
import json

reg_text = '''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\shell\osd_shell_command]
@="Download subtitles"

[HKEY_CLASSES_ROOT\Directory\shell\osd_shell_command\command]
@="\\"{}\\" \\"%1\\""
'''

def register_context_menu(application_path):
    global reg_text
    print "Install will launch regedit to register the Context menu..."

    path = application_path
    path = os.path.join(path, 'windows', 'download_subtitles.bat')
    path = path.replace('\\', '\\\\')

    reg_text = reg_text.format(path)

    fname = application_path
    fname = os.path.join(fname, 'windows', 'register_context_menu_for_osd.reg')
    with open(fname, 'w') as f:
        f.write(reg_text)

    #os.system("pause")
    os.system("start "+fname)
    #os.remove(fname)

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
    #print "Running from PyInstaller"
else:
    #print "Running from Python.exe"
    application_path = os.path.dirname(os.path.abspath(__file__))

application_path = os.path.abspath(os.path.join(application_path, '..'))

config_file = os.path.join(application_path, 'config', 'config.json')

if os.path.isfile(config_file):
    with open(config_file) as f:
        config = json.load(f)

print "************************************************************************"
print "Installing OSD..."
print ""

osub = OpenSubtitles()
login = False
while not login:
    print "Type your OpenSubtitle username:"
    user = raw_input("(Empty username will cancel the login):")
    if user == "":
        print "Cancelling the installation..."
        break

    password = raw_input("Type your opensubtitle password:")

    print "Checking login at OpenSubtitles.org..."
    token = osub.login(user, password)
    if token == None:
        print "ERROR! Invalid username/password. Could not login into OpenSubtitles.org"
        print ""
    else:
        print "Correct login. Login-out and procedding wiht the installation"
        login = True
        osub.logout()
        config['username'] = user
        config['password'] = password
        config['initial_path'] = ''

        with open(config_file, 'w') as f:
            str = json.dumps(config, indent=4, sort_keys=True)
            f.write(str)
        register_context_menu(application_path)

        print ""
        print "Installation finished!"
        print "************************************************************************"

os.system("pause")
