#-------------------------------------------------------------------------------
# Name:        osd (OpenSubtitlesDownloader)
# Purpose:
#
# Author:      Alex Porto
#
# Created:     27/09/2017
# Copyright:   (c) Alex Porto 2017
# Licence:     GPLv3
#-------------------------------------------------------------------------------

import os, sys
from pythonopensubtitles.opensubtitles import OpenSubtitles
import pythonopensubtitles.utils as osu
import urllib2
import subprocess
import shutil
import re
import difflib

failed_list = []

SUPORTED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.wmv', '.mkv']
MAX_DOWNLOADS_PER_DAY = 150 # Limit set by OpenSubtitles.org, to avoid leechs

download_counter = 0

def _erase_all_files_in_folder(path):
    for the_file in os.listdir(path):
        file_path = os.path.join(path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def _clean_file_name(file_name):
    for c in ['[', ']']:
        if c in file_name:
            file_name = file_name[:file_name.find(c)]

    file_name = file_name.strip()

    return file_name

def _search_by_imdb(video_file_name, language, osub):
    file_name = os.path.basename(video_file_name)
    file_name = os.path.splitext(file_name)[0]

    file_name = _clean_file_name(file_name)
    tv = re.findall(r"""(.*)[ .]S(\d{1,2})E(\d{1,2})[ .a-zA-Z]*(\d{3,4}p)?""", file_name, re.VERBOSE)
    if len(tv) == 0:
        name = file_name
        season = None
        episode = None
        print "(IMDB:", name + ",unknown season/episode)"
    else:
        name = tv[0][0]
        season = tv[0][1]
        episode = tv[0][2]
        print "(IMDB:", name + ", " + season + ", " + episode + ")",

    name = name.replace('.', ' ')
    name = name.replace('_', ' ')

    imdb_data = osub.search_movies_on_imdb(name)

    if not imdb_data.has_key('data'):
        return []

    if len(imdb_data['data']) == 0:
        return []

    if imdb_data['data'][0].has_key('id'):
        imdb_id = imdb_data['data'][0]['id']
    else:
        imdb_id = None

    if season and episode:
        if imdb_id:
            data = osub.search_subtitles([{'sublanguageid': language, 'imdbid': imdb_id, "season": season, 'episode': episode}])
        else:
            data = osub.search_subtitles([{'sublanguageid': language, 'movie name': name, "season": season, 'episode': episode}])
    else:
        if imdb_id:
            data = osub.search_subtitles([{'sublanguageid': language, 'imdbid': imdb_id}])
        else:
            data = osub.search_subtitles([{'sublanguageid': language, 'movie name': name}])

    return data

def _get_file_via_http(url, local_file_name):
    print "downloading...",

    path = os.path.dirname(__file__)
    sub_folder = os.path.join(path, 'temp_sub')
    zip_folder = os.path.join(path, 'temp_zip')
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)
    if not os.path.exists(zip_folder):
        os.makedirs(zip_folder)

    _erase_all_files_in_folder(sub_folder)
    _erase_all_files_in_folder(zip_folder)

    response = urllib2.urlopen(url)
    html = response.read()
    ext = os.path.splitext(url)[1]

    zip_file = os.path.join(zip_folder, 'subtitle' + ext)
    with open(zip_file, 'wb') as df:
        df.write(html)

    cmd = [r'C:\Program Files\7-Zip\7zG.exe', 'x', zip_file, '-o' + sub_folder]
    r = subprocess.check_call(cmd)

    srts = os.listdir(sub_folder)

    if len(srts) < 1:
        failed_list.append(video_file_name)
        print "-> No sub downloaded!"
        return

    in_file = os.path.join(sub_folder, srts[0])
    shutil.copyfile(in_file, local_file_name)

def _download_single_subtitle(video_file_name, languages, osub):
    global download_counter
    download_counter += 1
    if download_counter >= MAX_DOWNLOADS_PER_DAY:
        print "Daily downloads limit reached!"
        return False

    global failed_list
    print '\t' + os.path.basename(video_file_name),

    base_name = os.path.splitext(os.path.basename(video_file_name))[0]
    srt_name = os.path.join(os.path.dirname(video_file_name), base_name + ".srt")
    if os.path.isfile(srt_name):
        print "-> Already exists"
        return True

    f = osu.File(video_file_name)
    hash = f.get_hash()
    assert type(hash) == str
    size = f.size

    for language in languages:
        data = osub.search_subtitles([{'sublanguageid': language, 'moviehash': hash, 'moviebytesize': size}])
        if len(data) > 0:
            break

    if len(data) < 1:
        for language in languages:
            data = _search_by_imdb(video_file_name, language, osub)
            if len(data) > 0:
                break

    if len(data) < 1:
        failed_list.append(video_file_name)
        print "-> Not found"
        return True

    url = data[0]['SubDownloadLink']

    _get_file_via_http(url, srt_name)

    if os.path.isfile(srt_name):
        print "-> Success!"
    else:
        print "-> Failed"
        failed_list.append(video_file_name)

    return True

def _download_subtitles_at_path(path, osub, languages, recursive):
    print path + ":"
    files = os.listdir(path)
    for f in files:
        full_path = os.path.join(path, f)
        if os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            if ext in SUPORTED_VIDEO_EXTENSIONS:
                if _download_single_subtitle(full_path, languages, osub) == False:
                    return False

    for f in files:
        full_path = os.path.join(path, f)
        if os.path.isdir(full_path) and recursive:
            _download_subtitles_at_path(full_path, osub, languages, True)


    #print ""
    return True

def download_subtitles(initial_path, user, password, languages, recursive = True):
    osub = OpenSubtitles()
    token = osub.login(user, password)
    if token == None:
        print "---> Error. Invalid username/password. Please check your login information with OpenSubtitles.org"
        return False

    _download_subtitles_at_path(initial_path, osub, languages, recursive)

    osub.logout()

    with open(os.path.join(os.path.dirname(__file__), 'failed_list.txt'), 'w') as f:
        for item in failed_list:
            f.write("%s\n" % (item))
    return True

if __name__ == '__main__':
    if len(sys.argv) < 5:
        print "Usage: python osd.py <USERNAME> <PASSWORD> <MOVIES-FOLDER> <LANGUAGE-ID> [ALTERNATE-LANGUAGE-ID]..."
    else:
        username = sys.argv[1]
        password = sys.argv[2]
        path = sys.argv[3]
        languages = sys.argv[4:]

        download_subtitles(path, username, password, languages)

