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

reg_text = '''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\shell\osd_shell_command]
@="Download subtitles"

[HKEY_CLASSES_ROOT\Directory\shell\osd_shell_command\command]
@="\\"{}\\" \\"%1\\""
'''

import os, sys

if getattr(sys, 'frozen', False):
    # If the application is run as a bundle, the pyInstaller bootloader
    # extends the sys module by a flag frozen=True and sets the app
    # path into variable _MEIPASS'.
    application_path = sys._MEIPASS
    #print "Running from PyInstaller"
else:
    #print "Running from Python.exe"
    application_path = os.path.dirname(os.path.abspath(__file__))

#print application_path
path = application_path
path = os.path.join(path, 'download_subtitles.bat')
path = path.replace('\\', '\\\\')
#print path

reg_text = reg_text.format(path)

fname = application_path
fname = os.path.join(fname, 'register_context_menu_for_osd.reg')
with open(fname, 'w') as f:
    f.write(reg_text)

#os.system("pause")
os.system("start "+fname)
#os.remove(fname)



