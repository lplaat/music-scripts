from calls import api
import argparse
import shutil

parser = argparse.ArgumentParser(description='A loader for LeoDL Again')
parser.add_argument('--id', help='The deezer id from the artist or the album')
parser.add_argument('--album', help='Loads it as an album', action='store_true')
parser.add_argument('--artist', help='Loads it as an artist', action='store_true')
parser.add_argument('--list', help='Loads a list and loads it as a list of artists', action='store_true')
parser.add_argument('--nuke', help='Nukes the cache so everything is unloaded!', action='store_true')

args = parser.parse_args()

if args.nuke:
    print("You're about to nuke the cache. Type 'yes' to continue: ", end='')
    if input() == 'yes':
        print('Nuking the cache!')
        shutil.rmtree('./cache/deezer/')
    else:
        print('Aborting!')
else:
    if args.list:
        with open('list.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
            for line in lines:
                if not line == '\n':
                    id = int(line.split(' ')[0])
                    api.deezer.loadTracksFromArtist(id)
                    print(f"Just loaded {id}!")
    elif not args.id:
        print("Error: The 'id' argument is required unless using --nuke or --list.")
        parser.print_help()
    else:
        if args.album:
            api.deezer.loadTracksFromAlbum(args.id)
            print('Done!')
        else:
            api.deezer.loadTracksFromArtist(args.id)
            print('Done!')
