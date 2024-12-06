from calls import api
from calls import cache 
from alive_progress import alive_bar
import os
import mutagen.mp4
from dotenv import load_dotenv

# Load .env File
load_dotenv()

# Mapper
artists = []
tracks = {}
folders = os.listdir(os.getenv('IPOD_MUSIC_PATH'))
with alive_bar(len(folders)) as bar:
    for folder in folders:
        for folderTwo in os.listdir(os.getenv('IPOD_MUSIC_PATH') + '/' + folder):
            for file in os.listdir(os.getenv('IPOD_MUSIC_PATH') + '/' + folder + '/' + folderTwo):
                path = os.getenv('IPOD_MUSIC_PATH') + '/' + folder + '/' + folderTwo + '/' + file
                
                if 'cover.jpg' != file:
                    try:
                        audio = mutagen.mp4.MP4(path)
                        
                        tracks[audio['\xa9alb'][0] + audio['\xa9nam'][0] + audio['\xa9ART'][0]] = path
                        
                        if not audio['\xa9ART'][0] in artists:
                            artists.append(audio['\xa9ART'][0])
                    except:
                        print('Failed to load: ' + path)
                    
        bar()
caches = cache.deezer.returnAllCaches()

print('Done mapping...')

# Generating top 50 playlists
with alive_bar(len(artists)) as bar:
    for artistName in artists:                
        withDupesArtistTracks = []
        for cacheData in caches:
            if not cacheData['url'].find('/track/') == -1:
                track = api.deezer.call(cacheData['url'])
                context = cache.deezer(cacheData['url']).get('context')

                try:
                    path = tracks[track['album']['title'] + track['title'] + artistName]
                except KeyError:
                    continue
                
                if not 'ytViews' in context.keys():
                    continue
                else:
                    if context['ytViews'] == None:
                        continue
                
                withDupesArtistTracks.append([context['ytViews'], path, track['title'], context['ytId']])
                                
        artistTracks = []
        for trackA in withDupesArtistTracks:
            found = False
            for trackB in artistTracks:
                if trackA[2] == trackB[2] or trackA[3] == trackB[3]:
                    found = True
                    break

                if os.getenv('ALLOW_REMIX_IN_PLAYLIST') == 'false' and not trackA[2].lower().find('remix') == -1:
                    found = True
                    break
                
            if not found:
                artistTracks.append(trackA)
                                
        artistTracks.sort(key=lambda item: item[0], reverse=True)

        lines = ["#EXTM3U"]
        for track in artistTracks[0:50]:
            lines.append(track[1][3:])
        open(os.getenv('IPOD_PLAYLIST_PATH') + '/Top 50 - ' + artistName + '.m3u', 'w', encoding='utf-8').write('\n'.join(lines))
        bar()
        
print('Done generating top tracks!')