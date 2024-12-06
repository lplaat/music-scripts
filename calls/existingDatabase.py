from dotenv import load_dotenv
import os
import subprocess
import shutil
from mutagen.easyid3 import EasyID3
from mutagen.flac import FLAC
from calls import cache
from dotenv import load_dotenv

# Load .env File
load_dotenv()

# Load .env File
load_dotenv()

def getMetadata(path):
    # Returns valid audio metadata
    try:
        if path.lower().endswith('.mp3'):
            audio = EasyID3(path)
        elif path.lower().endswith('.flac'):
            audio = FLAC(path)
        elif path.lower().endswith('.m4a'):
            audio = EasyID3(path)
        else:
            return None
    except Exception as e:
        print(f'Failed to load: {path} because: {e}')
        return None
    return audio

def returnAllTracks(path):
    # Returns a list of all tracks in path provided
    tracks = []
    for filename in os.listdir(path):
        newPath = path + filename
        if os.path.isdir(newPath):
            # Crawls over all dirs
            tracks += returnAllTracks(newPath + '/')
        else:
            # Parse audio data
            audio = getMetadata(newPath)
            
            if not audio == None:
                tracks.append({
                    'path': newPath,
                    'title': audio["title"][0],
                    'artist': audio["artist"][0],
                    'album': audio["album"][0],
                })
                
    return tracks

def getFilePathFromHash(hash):
    # Returns a cache path from a hash
    path = f'./cache/audio/{hash[0:2]}/'
    for file in os.listdir(path):
        if file.split('.')[0] == hash:
            return path + file
    return None

def transferFileToCache(track):
    # Transfers track to the cache database
    hash = cache.tools.sha1(track['path'] + track['title'])
    
    # Make destination path
    destinationPath = f'{os.getcwd()}/cache/audio/{hash[0:2]}/'
    os.makedirs(destinationPath, exist_ok=True)
    destinationPath += f'{hash}.m4a'
    
    # Check if file already exists
    if not getFilePathFromHash(hash) == None:
        return hash, False
    
    # Transfer file with encoding if allowed
    if os.getenv('FORCE_TRANSCODING') == 'true':
        subprocess.run([
            "ffmpeg",
            "-i", track['path'],
            "-map", "0:a",
            "-c:a", "aac",
            "-strict", "experimental",
            "-b:a", "192k",
            destinationPath,
            "-y"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        shutil.copyfile(track['path'], destinationPath)

    return hash, True

def copyFile(hash, toPath):
    # Gets the file from the hash and copies it to the path
    mainPath = getFilePathFromHash(hash)
    shutil.copy(mainPath, toPath)