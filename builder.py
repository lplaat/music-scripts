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

# Load .env File
load_dotenv()

def cleaner(path):
    # Cleans the path off downloaded stuff
    path = path.replace('<', '_').replace('>', '_').replace(':', '_').replace('\"', '_').replace('/', '_').replace('.', '_')
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
    # if 'existingAudioHash' in context.keys():
    #     existingDatabase.copyFile(context['existingAudioHash'], filePath)
    # else:
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

    if album['record_type'] == 'single' or album['nb_tracks'] <= 2:
        audio['aART'] = "Singles"
    else:
        audio['aART'] = artist['name']

    audio['\xa9nam'] = track['title']
    audio['\xa9ART'] = artist['name']
    audio['\xa9alb'] = album['title']
    audio['\xa9day'] = track['release_date'].split('-')[0]
    audio['trkn'] = [ ( track['track_position'], album['nb_tracks']) ]
    audio['cprt'] = album['label']

    genres = []
    for genre in album['genres']['data']: 
        genres.append(genre['name'])
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