from calls import easyThreader
from calls import cache
from calls import api
from calls import existingDatabase
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import mutagen.mp4
from alive_progress import alive_bar
import os
import argparse

# Load .env File
load_dotenv()

# Setup argparse
parser = argparse.ArgumentParser(description='Builds music library with metadata.')
parser.add_argument('--mode', help='The build mode (ipod or navidrome)', default='ipod', choices=['ipod', 'navidrome'])
args = parser.parse_args()

def cleaner(path):
    # Cleans the path off downloaded stuff
    path = path.replace('<', '_').replace('>', '_').replace(':', '_').replace('"', '_').replace('/', '_').replace('.', '_')
    return path.replace('\\', '_').replace('|', '_').replace('?', '_').replace('*', '_')

def copiers(url):
    # Copies music file with right metadata
    track = api.deezer.call(url)
    context = cache.deezer(url).get(filetype='context')
    album = api.deezer.call(f"/album/{track['album']['id']}")
    
    if not 'mainArtistId' in context.keys():
        artistId = album['artist']['id']
    else:
        artistId = context['mainArtistId']
    
    artist = api.deezer.call(f"/artist/{artistId}")
    
    parentPath = f"./build/{cleaner(artist['name'])}/{cleaner(album['title'])}/"
    filePath = parentPath + f"{cleaner(track['title'])}.m4a"
    
    # Checking that all the files are downloaded before making the path
    if not 'ytId' in context.keys() and not 'existingAudioHash' in context.keys():
        return False
    
    if not 'existingAudioHash' in context.keys():
        _, exist = cache.youtube.returnPathToSaveAudio(context['ytId'], 'm4a')
        if not exist:
            return False
    
    # Stops if file is already downloaded
    if os.path.exists(filePath):
        return False
    
    # Making path and copy files over
    os.makedirs(parentPath, exist_ok=True)
    
    # Check if there is a existing audio file
    if 'existingAudioHash' in context.keys():
        existingDatabase.copyFile(context['existingAudioHash'], filePath)
    else:
        api.youtube.copyFile(context['ytId'], filePath)
    
    # Copy over album cover
    if not os.path.exists(parentPath + 'cover.jpg'):
        coverBytes = api.deezer.call(album['cover_medium'], filetype='bytes')
        image = Image.open(BytesIO(coverBytes))
        image.save(parentPath + 'cover.jpg', 'JPEG', quality=95, baseline=0)

    # Applying metadata
    try:
        audio = mutagen.mp4.MP4(filePath)
    except:
        print(f'Failed to load: {filePath}')
        return False

    if args.mode == 'ipod':
        if album.get('record_type') == 'single' or album.get('nb_tracks', 0) <= 2:
            audio['aART'] = "Singles"
        else:
            audio['aART'] = artist['name']
        audio['\xa9ART'] = artist['name']
    elif args.mode == 'navidrome':
        artists_list = []
        if 'contributors' in track and track['contributors']:
            for contributor in track['contributors']:
                artists_list.append(contributor['name'])
        
        if artists_list:
            audio['\xa9ART'] = '; '.join(artists_list)
        else:
            audio['\xa9ART'] = artist['name']

        if 'artist' in album and 'name' in album['artist']:
            audio['aART'] = album['artist']['name']
        else:
            audio['aART'] = artist['name']

    audio['\xa9nam'] = track['title']
    audio['\xa9alb'] = album['title']
    if 'release_date' in track and track['release_date']:
        audio['\xa9day'] = track['release_date'].split('-')[0]
    if 'track_position' in track and 'nb_tracks' in album:
        audio['trkn'] = [ ( track['track_position'], album['nb_tracks']) ]
    if 'label' in album:
        audio['cprt'] = album['label']

    genres = []
    if 'genres' in album and 'data' in album['genres']:
        for genre in album['genres']['data']: 
            genres.append(genre['name'])
    if genres:
        audio['\xa9gen'] = '; '.join(genres)

    # Applying cover to file
    with open(parentPath + 'cover.jpg', "rb") as album_cover_file:
        album_cover_data = album_cover_file.read()
        audio["covr"] = [album_cover_data]
    
    audio.save()

# Looks for track caches and run the copier function
multiThreads = easyThreader.instance(copiers, maxThreads=int(os.getenv('COPIER_THREADS')))
caches = cache.deezer.returnAllCaches()
with alive_bar(len(caches)) as bar:
    for cacheData in caches:
        if not cacheData['url'].find('/track/') == -1:
            multiThreads.run(cacheData['url'])
            
        bar()

multiThreads.stop()
