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
import json
import time
import datetime

failed_list = []
skipped_files = 0

SUPORTED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.wmv', '.mkv']
TAG_LIST = ['hdtv', '1080', '720', 'x264', 'amzn', 'webrip', 'repack', 'proper',
            'xvid', '480', 'aac', 'youtube', 'dvdrip', 'bluray', 'bdrip', '2hd',
            'internal', 'pdtv', 'brrip']
MAX_DOWNLOADS_PER_DAY = 150 # Limit set by OpenSubtitles.org, to avoid leechs

#download_counter = 0

failed_list_file = os.path.join(os.path.dirname(__file__), 'config', 'failed_list.txt')
config_file = os.path.join(os.path.dirname(__file__), 'config', 'config.json')
config = {
    'last_download_date':None,
    'today_download_count':0,
    'username':'',
    'password':'',
    'languages': [],
    'initial_path': ''}

def _append_failed_file(video_file_name):
    if os.path.isfile(failed_list_file):
        with open(failed_list_file, 'a') as f:
            f.write(video_file_name + '\n')
    else:
        with open(failed_list_file, 'w') as f:
            f.write(video_file_name + '\n')

def _erase_all_files_in_folder(path):
    '''
    Remove all files for a given directory
    Used to clean the temp download folders before downloading or
    extracting new subtitles
    '''
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
    '''
    Clean up a video file name, removing ripper tags and other useless text
    that could prevent identifying the correct movie name from it
    '''

    # Remove useless characters
    for c in ['[', ']', '_']:
        if c in file_name:
            file_name = file_name[:file_name.find(c)]

    # Remove dots/period when used as white-spaces
    if file_name.count('.') > 1:
        file_name = file_name.replace('.', ' ')

    for tag in TAG_LIST:
        if tag in file_name.lower():
            file_name = file_name[:file_name.lower().find(tag)]

    file_name = file_name.strip()

    return file_name

def _search_by_imdb(video_file_name, language, osub):
    '''
    Extrace search info from video file name (name, episode, season, etc)
    Use this info on imdb.com to correctly identify the video file
    '''
    file_name = os.path.basename(video_file_name)
    file_name = os.path.splitext(file_name)[0]

    file_name = _clean_file_name(file_name)
    tv = re.findall(r"""(.*)[ .]S(\d{1,2})E(\d{1,2})[ .a-zA-Z]*(\d{3,4}p)?""", file_name, re.VERBOSE)
    if len(tv) == 0:
        name = file_name
        season = None
        episode = None
        print "(IMDB:", name + ",unknown season/episode)",
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
            # Best info available for searching
            # imdb id found: Use it for the search
            # season and episode also used on search
            data = osub.search_subtitles([{'sublanguageid': language, 'imdbid': imdb_id, "season": season, 'episode': episode}])
        else:
            # 2nd best search info
            # imdb id not found: Try searching for the movie/series name identified from the filename
            # imdb id found: Use it for the search
            data = osub.search_subtitles([{'sublanguageid': language, 'movie name': name, "season": season, 'episode': episode}])
    else:
        if imdb_id:
            # Not so good search info
            # imdb id found: Use it for the search
            # seasong and episode not available
            data = osub.search_subtitles([{'sublanguageid': language, 'imdbid': imdb_id}])
        else:
            # Worst info for searching
            # No imdb id, no season/episode.
            # Try searching using only the movie/series name extracted from the filename
            data = osub.search_subtitles([{'sublanguageid': language, 'movie name': name}])
    return data

def _save_config():
    with open(config_file, 'w') as f:
        json.dump(config, f)

def _get_file_via_http(url, local_file_name):
    '''
    Download the compressed subtitle from web, and unzip it
    '''
    #global download_counter
    #download_counter += 1
    config['today_download_count'] = config['today_download_count'] + 1
    _save_config()
    print "downloading (%d)..." % (config['today_download_count']),

    path = os.path.dirname(__file__)
    sub_folder = os.path.join(path, 'temp_sub')
    zip_folder = os.path.join(path, 'temp_zip')
    if not os.path.exists(sub_folder):
        os.makedirs(sub_folder)
    if not os.path.exists(zip_folder):
        os.makedirs(zip_folder)

    _erase_all_files_in_folder(sub_folder)
    _erase_all_files_in_folder(zip_folder)

    ext = os.path.splitext(url)[1]
    try:
        response = urllib2.urlopen(url)
        html = response.read()
    except:
        _append_failed_file(video_file_name)
        print "-> download failed!"
        return False

    zip_file = os.path.join(zip_folder, 'subtitle' + ext)
    with open(zip_file, 'wb') as df:
        df.write(html)

    cmd = [r'C:\Program Files\7-Zip\7zG.exe', 'x', zip_file, '-o' + sub_folder]
    r = subprocess.check_call(cmd)

    srts = os.listdir(sub_folder)

    if len(srts) < 1:
        _append_failed_file(video_file_name)
        print "-> No sub downloaded!"
        return False

    in_file = os.path.join(sub_folder, srts[0])
    shutil.copyfile(in_file, local_file_name)

def _download_single_subtitle(video_file_name, srt_name, languages, osub):
    #global download_counter
    if config['today_download_count'] >= MAX_DOWNLOADS_PER_DAY:
        print "Daily downloads limit reached!"
        return False

    print '\t' + os.path.basename(video_file_name),

    f = osu.File(video_file_name)
    hash = f.get_hash()
    assert type(hash) == str
    size = f.size

    # Try searching for a subtitle created by this exact video file, using hash
    for language in languages:
        try:
            data = osub.search_subtitles([{'sublanguageid': language, 'moviehash': hash, 'moviebytesize': size}])
        except:
            data = []
        if len(data) > 0:
            break

    # No subtitle found for this file, try searching using IMDB information
    if len(data) < 1:
        for language in languages:
            try:
                data = _search_by_imdb(video_file_name, language, osub)
            except:
                data = []
            if len(data) > 0:
                break

    # No subtitle found using the provided information: Give up to try the next file
    if len(data) < 1:
        _append_failed_file(video_file_name)
        print "-> Not found"
        return True

    url = data[0]['SubDownloadLink']

    # Try downloading the file
    _get_file_via_http(url, srt_name)

    # Finally, check if the expected file was correctly created
    if os.path.isfile(srt_name):
        print "-> Success!"
    else:
        print "-> Failed"
        _append_failed_file(video_file_name)

    return True

def _download_subtitles_at_path(path, osub, languages, recursive):
    '''
    Search all subdirectories, recursivelly, calling the function
    that downloads a subtitle whenever a video file is found
    '''
    global skipped_files
    files = os.listdir(path)
    files_to_search = []
    for f in files:
        full_path = os.path.join(path, f)
        if full_path in failed_list:
            skipped_files += 1
            # Skiiping file that was already checked and failed
            continue

        if os.path.isfile(full_path):
            ext = os.path.splitext(full_path)[1].lower()
            if ext in SUPORTED_VIDEO_EXTENSIONS:
                base_name = os.path.splitext(os.path.basename(full_path))[0]
                srt_name = os.path.join(os.path.dirname(full_path), base_name + ".srt")
                if not os.path.isfile(srt_name):
                    files_to_search.append((full_path, srt_name))
                else:
                    skipped_files += 1

    if len(files_to_search) > 0:
        print path
        for f in files_to_search:
            if _download_single_subtitle(f[0], f[1], languages, osub) == False:
                return False

    for f in files:
        full_path = os.path.join(path, f)
        if os.path.isdir(full_path) and recursive:
            _download_subtitles_at_path(full_path, osub, languages, True)

    return True

def download_subtitles(initial_path, user, password, languages, recursive = True):
    '''
    Logins into opensubtitles.org and start the recursive search
    '''
    global config
    global failed_list

    if os.path.isfile(config_file):
        with open(config_file) as f:
            config = json.load(f)

    today = datetime.date.today().strftime("%Y%m%d")
    if config['last_download_date'] != today:
        config['last_download_date'] = today
        config['today_download_count'] = 0

    config['username'] = user
    config['password'] = password
    config['languages'] = languages
    config['initial_path'] = languages
    _save_config()

    if os.path.isfile(failed_list_file):
        with open(failed_list_file) as f:
            failed_list = f.readlines()
            failed_list = [x.strip() for x in failed_list]

    osub = OpenSubtitles()
    token = osub.login(user, password)
    if token == None:
        print "---> Error. Invalid username/password. Please check your login information with OpenSubtitles.org"
        return False

    _download_subtitles_at_path(initial_path, osub, languages, recursive)

    osub.logout()

    print "Done!\n%d video files not considered during this search\n(Either already had subtitle or had failed in a previous search)" % (skipped_files)

    #$with open(failed_list_file, 'w') as f:
    #    for item in failed_list:
    #        f.write("%s\n" % (item))
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

