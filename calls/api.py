import requests
import json
from calls import cache
import os
import time
from dotenv import load_dotenv
from ytmusicapi import YTMusic
import subprocess
import math
import shutil

# Load .env File
load_dotenv()

#Simple things to call
class tools():
    def allWaysPositive(i):
        # Returns a value that is always positive
        if i < 0: return i - i - i
        return i
    
    def convertViewCount(view_string):
        if not view_string:
            return 0
        
        view_string = view_string.strip().lower()
        
        if view_string.isdigit():
            return int(view_string)
        
        multipliers = {
            'k': 1000,
            'm': 1000000,
            'b': 1000000000
        }
        
        number = ''
        suffix = ''
        for char in view_string:
            if char.isdigit() or char == '.':
                number += char
            else:
                suffix = char
                break
        
        try:
            number = float(number)
            if suffix in multipliers:
                number *= multipliers[suffix]
            return int(number)
        except ValueError:
            return 0

# Call deezer api
class deezer():
    def call(pathOrUrl, filetype='json', noCache=False, noSavingCache=False):
        # Checks if there already is a host name available
        if pathOrUrl.find('https://') == -1:
            url = 'https://api.deezer.com' + pathOrUrl
        else:
            url = pathOrUrl
        
        # Check for a cache version
        cacheInstance = cache.deezer(url=url)
        realRequest = False
        if not noCache or not noSavingCache:
            if cacheInstance.exist():
                data = cacheInstance.get()
            else:
                realRequest = True
        else:
            realRequest = True
        
        # Request newest version and store it
        if realRequest:
            for _ in range(int(os.getenv('REQUESTS_AMOUNTS'))):
                response = requests.get(url)
                
                if filetype == 'json':
                    data = json.loads(response.content)
                    
                    if not 'error' in data.keys():
                        if not noSavingCache: cacheInstance.save(data, filetype=filetype)
                        return data
                    else:
                        time.sleep(1)

                elif filetype == 'bytes':
                    if response.status_code == 200:
                        data = response.content
                        if not noSavingCache: cacheInstance.save(data, filetype=filetype)
                        return data
            
            raise ConnectionError(f"Failed {os.getenv('REQUESTS_AMOUNTS')} times to get the url: {url}") 
        
        # Return response
        return data
    
    def loadTracksFromAlbum(id, mainArtistId=None):
        # Loads tracks metadata and loads tracks metadata
        album = deezer.call('/album/' + str(id))
        deezer.call(album['cover_medium'], filetype='bytes')

        next = f'/album/{id}/tracks?index='
        index = 0
        while True:
            tracks = deezer.call(next + str(index))['data']
            for track in tracks:
                deezer.call('/track/' + str(track['id']))
                
                if not mainArtistId == None:
                    cache.deezer('/track/' + str(track['id'])).setValue('mainArtistId', mainArtistId)

            index += 25
            if len(tracks) == 0:
                break    

    def loadTracksFromArtist(id):
        # Loading album pages and requests them     
        next = f'/artist/{id}/albums?index='
        index = 0
        while True:
            page = deezer.call(next + str(index), noCache=True, noSavingCache=True)
            for album in page['data']:
                # Requests all tracks data
                deezer.call('/album/' + str(album['id']))
                deezer.loadTracksFromAlbum(album['id'], mainArtistId=id)
            
            index += 25
            if len(page['data']) == 0:
                break        
            
# Call ytd-lp
ytmusic = YTMusic()
class youtube():
    def searchForBestMatch(quarry, duration):
        # Find the right video that match the music metadata with yt music
        results = ytmusic.search(quarry, filter="songs")
        bestViews = 0        
        bestScore = math.inf
        bestYoutubeId = None

        i = 0
        for video in results:
            if video['videoType'] == 'MUSIC_VIDEO_TYPE_ATV':
                if 'views' in video.keys():
                    if tools.convertViewCount(video['views']) > bestViews:
                        bestViews = tools.convertViewCount(video['views'])

                score = tools.allWaysPositive(duration - video['duration_seconds']) + int(os.getenv('PUNISHING_POINTS')) * i
                if not video['isExplicit']:
                    score += 10

                if bestScore > score:
                    bestScore = score
                    bestYoutubeId = video['videoId']

            i += 1

        return bestYoutubeId, bestViews

    def searchForBestMatchOld(quarry, duration):
        # Find the right video that match the music metadata
        command = [
            'yt-dlp',
            f'ytsearch10:"{quarry}"',
            '--dump-json',
            '--quiet',
            '--no-warnings'
        ]
        
        # Fetches youtube search data
        bestScore = math.inf
        bestYoutubeId = None
        bestViews = 0
        
        i = 0
        with subprocess.Popen(command, stdout=subprocess.PIPE) as searchProcess:
            while searchProcess.poll() is None:
                line = searchProcess.stdout.readline().decode()
                try:
                    data = json.loads(line)
                    if data['duration'] > 900:
                        continue
                    
                    score = tools.allWaysPositive(duration - data['duration']) + int(os.getenv('PUNISHING_POINTS')) * i
                    if bestScore > score:
                        bestScore = score
                        bestYoutubeId = data['id']

                    if i < 3 and bestViews < data['view_count']:
                        bestViews = data['view_count']
                        
                    i += 1
                except json.decoder.JSONDecodeError:
                    pass
                
        return bestYoutubeId, bestViews
    
    def downloadYoutubeAudio(ytID):
        # Download audio only from video to the path given
        path, exist = cache.youtube.returnPathToSaveAudio(ytID, 'm4a')
        
        if not exist:
            for _ in range(2):
                try:
                    subprocess.check_output(
                        ['yt-dlp', f'https://www.youtube.com/watch?v={ytID}', '-f', 'bestaudio[ext=m4a]', '--no-warnings', '--quiet', '-o', path],
                    )
                    return True
                except:
                    pass
            print('Failed to donwload!')
            
        return False
    
    def copyFile(ytID, destPath):
        # Copies yt audio to path
        path, exist = cache.youtube.returnPathToSaveAudio(ytID, 'm4a')
        
        if exist:
            shutil.copyfile(path, destPath)