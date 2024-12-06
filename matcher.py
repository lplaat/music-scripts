from calls import cache
from calls import api
from calls import easyThreader
from calls import existingDatabase
import os
from dotenv import load_dotenv
from alive_progress import alive_bar
import argparse

# Load .env File
load_dotenv()

# Create worker function
def youtubeDownloader(url):
    # Get track information
    data = api.deezer.call(url)
    
    artists = []
    for artist in data['contributors']:
        artists.append(artist['name'])
    
    quarry = ', '.join(artists) + ' - ' + data['title']
    
    context = cache.deezer(url).get(filetype='context')
    # if 'ytId' in context.keys():
    #     _, exist = cache.youtube.returnPathToSaveAudio(context['ytId'], 'm4a')
    #     if exist:
    #         return None
    #     else:
    #         id = context['ytId']
    # else:
    id, views = api.youtube.searchForBestMatch(quarry, data['duration'])
    if not id == None:
        cache.deezer(url).setValue('ytId', id)
        cache.deezer(url).setValue('ytViews', views)

    if not id == None:
        downloaded = api.youtube.downloadYoutubeAudio(id)
        
        if downloaded:
            print('Downloaded: ' + quarry)

def directCopier(url, loadedTracks):
    # Get track information
    data = api.deezer.call(url)

    for track in loadedTracks:
        if not (track['artist'].lower() == data['contributors'][0]['name'].lower() and track['album'].lower() == data['album']['title'].lower() and track['title'].lower() == data['title'].lower()):
            # print(track['artist'], data['contributors'][0]['name'], track['artist'] == data['contributors'][0]['name'])
            # print(track['album'], data['album']['title'], track['album'] == data['album']['title'])
            # print(track['title'], data['title'], track['title'] == data['title'])
            continue
            
        if not(track['artist'].split(', ')[0].lower() == data['contributors'][0]['name'].lower()):
            continue
        
        hash, success = existingDatabase.transferFileToCache(track)
        cache.deezer(url).setValue('existingAudioHash', hash)
        if hash == None or not success:
            break
        
        artists = []
        for artist in data['contributors']:
            artists.append(artist['name'])
            
        print('Transferred: ' + ', '.join(artists) + ' - ' + data['title'])
        break

parser = argparse.ArgumentParser(description='Matches metadata with audio files')
parser.add_argument('--youtube', help='Searches for tracks on youtube', action='store_true')
parser.add_argument('--localData', help='Searches for tracks on local file system', action='store_true')

args = parser.parse_args()

if args.youtube:
    multiThreads = easyThreader.instance(youtubeDownloader, maxThreads=int(os.getenv('YOUTUBE_MATCHER_THREADS')))

    # Looks for track caches and gives it to the different threads
    caches = cache.deezer.returnAllCaches()
    with alive_bar(len(caches)) as bar:
        for cacheData in caches:
            if not cacheData['url'].find('/track/') == -1:
                multiThreads.run(cacheData['url']),
            bar()

    multiThreads.stop()
else:
    if args.localData:
        # Loads all other downloaded tracks from the different path and compare them to loaded tracks
        tracks = existingDatabase.returnAllTracks(os.getenv('EXISTING_DATABASE_PATH'))
        print(f'Using {len(tracks)} amount of existing tracks')
        
        multiThreads = easyThreader.instance(directCopier, maxThreads=int(os.getenv('COPIER_THREADS')))
        
        caches = cache.deezer.returnAllCaches()
        with alive_bar(len(caches)) as bar:
            for cacheData in caches:
                if not cacheData['url'].find('/track/') == -1:
                    multiThreads.run(cacheData['url'], tracks),
                bar()
                
        multiThreads.stop()
    else:
        print('Please use one of the functions!')