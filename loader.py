from calls import api
import argparse
import shutil
import os

def nuke_cache():
    """Removes the deezer cache directory."""
    cache_dir = './cache/deezer/'
    if not os.path.exists(cache_dir):
        print("Cache directory not found. Nothing to nuke.")
        return

    print("You're about to nuke the Deezer cache. This is irreversible.")
    confirm = input("Type 'yes' to continue: ")
    if confirm.lower() == 'yes':
        print('Nuking the cache...')
        try:
            shutil.rmtree(cache_dir)
            print('Cache nuked successfully.')
        except OSError as e:
            print(f"Error removing cache: {e}")
    else:
        print('Aborting!')

def load_from_list(filepath):
    """Loads artist IDs from a text file."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        print(f"Loading artists from {filepath}...")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            try:
                artist_id = int(line.split(' ')[0])
                print(f"Loading artist ID: {artist_id}")
                api.deezer.loadTracksFromArtist(artist_id)
                print(f"Successfully loaded artist {artist_id}.")
            except (ValueError, IndexError):
                print(f"Skipping invalid line: {line}")
        print("Finished loading from list.")
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found.")

def load_id(load_type, deezer_id):
    """Loads tracks for a single album or artist ID."""
    print(f"Loading {load_type} with ID: {deezer_id}...")
    if load_type == 'album':
        api.deezer.loadTracksFromAlbum(deezer_id)
    elif load_type == 'artist':
        api.deezer.loadTracksFromArtist(deezer_id)
    print('Done!')

def main():
    parser = argparse.ArgumentParser(
        description='A smart loader for Deezer data for LeoDL Again.',
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument('--nuke', action='store_true', help='Nuke the Deezer cache so everything is re-downloaded.')
    action_group.add_argument('--from-list', metavar='FILE', help='Load artist IDs from a specified text file.')
    action_group.add_argument('--id', metavar='DEEZER_ID', help='The Deezer ID for an artist or album.')

    parser.add_argument(
        '--type',
        choices=['artist', 'album'],
        help="Specify the type of the ID ('artist' or 'album'). Required when using --id."
    )

    args = parser.parse_args()

    if args.id and not args.type:
        parser.error("--type is required when using --id.")

    if args.nuke:
        nuke_cache()
    elif args.from_list:
        load_from_list(args.from_list)
    elif args.id:
        load_id(args.type, args.id)

if __name__ == "__main__":
    main()