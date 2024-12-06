# Music Scripts

This collection of scripts helps manage a large music library for iPods and other devices.  
**Note:** This program is not fully documented and requires some terminal or programming knowledge.

## Installation Requirements

1. Clone the repository:
   ```bash
   git clone git@github.com:lplaat/music-scripts.git
   ```
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a .env folder with all proper settings. For more information look in `.env.example` or in the readme

## Script Overview

### General Scripts
- **`loader.py`**  
  Loads artists or albums using a Deezer ID.

- **`matcher.py`**  
  Finds matching music from YouTube (Music) or local libraries. Results are cached for faster future use.

- **`builder.py`**  
  Creates the final music folder with organized tracks and metadata.

### iPod Custom Scripts
- **`playlist.py`**  
  Generates `.m3u8` playlist files for each artist. The playlists prioritize the most viewed YouTube videos, using metadata retrieved by `matcher.py`.

- **`transfer.py`**  
  Transfers files from one path to another, performing checks to ensure correctness during the process.


## Environment Variable Documentation

| Variable                  | Description                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------|
| **`REQUESTS_AMOUNTS`**    | Number of requests sent to the Deezer API before the program halts.                                  |
| **`YOUTUBE_MATCHER_THREADS`** | Number of threads used by `matcher.py` to scan YouTube for the correct music source.              |
| **`PUNISHING_POINTS`**    | Determines how closely a YouTube result matches the music's length and rank. Default: `7`.           |
| **`COPIER_THREADS`**      | Number of threads `matcher.py` uses to copy music from local storage to the cache.                   |
| **`EXISTING_DATABASE_PATH`** | Path to an existing library of raw music with metadata.                                           |
| **`FORCE_TRANSCODING`**   | Forces transcoding of all existing media using `ffmpeg`. Ensure `ffmpeg` is in your system's PATH.   |

### iPod-Specific Variables

| Variable                  | Description                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------|
| **`IPOD_MUSIC_PATH`**     | Path to the iPod's music directory.                                                                 |
| **`IPOD_PLAYLIST_PATH`**  | Path to the source `.m3u8` file used by Rockbox.                                                    |
| **`ALLOW_REMIX_IN_PLAYLIST`** | Whether remixes are allowed in the generated playlists. (Set to `True` or `False`)              |


## Notes

- **Accuracy**: The scripts attempt to match and organize music automatically but may require manual adjustments.  
- **Dependencies**: Ensure `ffmpeg` is installed and accessible via your system's PATH.  
- **Customization**: Adjust environment variables as needed to tailor the scripts to your requirements.
- **Maintenance**: This project is not actively maintained. It was originally built for personal use, but if you find it useful, feel free to explore it.