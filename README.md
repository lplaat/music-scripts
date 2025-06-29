# Music Scripts

This collection of scripts helps manage a large music library for iPods, Navidrome, and other devices.  
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
3. Create a `.env` file with the proper settings. Refer to `.env.example` for a template.

## Script Overview

### General Scripts
- **`loader.py`**  
  Loads artists or albums from Deezer using a variety of methods. It can take a Deezer ID, a list of IDs from a file, or nuke the cache to start fresh.

- **`matcher.py`**  
  Finds matching music from YouTube Music or your local library. Results are cached for faster future use.

- **`builder.py`**  
  Builds the final music library with organized tracks and metadata. It supports two modes: `ipod` and `navidrome`.

### iPod-Specific Scripts
- **`playlist.py`**  
  Generates `.m3u` playlist files for each artist. The playlists prioritize the most viewed YouTube videos, using metadata retrieved by `matcher.py`.

- **`transfer.py`**  
  Transfers files from one path to another, performing integrity checks to ensure correctness.

## Usage Examples

### `loader.py`

- **Load a single artist or album by ID:**
  ```bash
  python3 loader.py --id <DEEZER_ID> --type <artist|album>
  ```

- **Load multiple artists from a file:**
  ```bash
  python3 loader.py --from-list list.txt
  ```

- **Clear the Deezer cache:**
  ```bash
  python3 loader.py --nuke
  ```

### `builder.py`

- **Build for an iPod:**
  ```bash
  python3 builder.py --mode ipod
  ```

- **Build for Navidrome:**
  ```bash
  python3 builder.py --mode navidrome
  ```

## Environment Variable Documentation

| Variable                  | Description                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------|
| **`REQUESTS_AMOUNTS`**    | Number of times to retry a request to the Deezer API before failing.                                  |
| **`YOUTUBE_MATCHER_THREADS`** | Number of threads used by `matcher.py` to find matching tracks on YouTube.              |
| **`PUNISHING_POINTS`**    | A penalty score added to a track match based on its position in the search results. Default: `7`.           |
| **`COPIER_THREADS`**      | Number of threads used by `matcher.py` to copy music from local storage to the cache.                   |
| **`EXISTING_DATABASE_PATH`** | Path to an existing library of music files with metadata.                                           |
| **`FORCE_TRANSCODING`**   | If `true`, forces all local files to be transcoded to AAC using `ffmpeg`.   |

### iPod-Specific Variables

| Variable                  | Description                                                                                          |
|---------------------------|------------------------------------------------------------------------------------------------------|
| **`IPOD_MUSIC_PATH`**     | Path to the iPod's music directory.                                                                 |
| **`IPOD_PLAYLIST_PATH`**  | Path where the generated `.m3u` playlist files will be saved.                                                    |
| **`ALLOW_REMIX_IN_PLAYLIST`** | If `false`, remixes will be excluded from the generated playlists.              |

## Notes

- **Accuracy**: The scripts attempt to match and organize music automatically but may require manual adjustments.  
- **Dependencies**: Ensure `ffmpeg` is installed and accessible in your system's PATH if you enable `FORCE_TRANSCODING`.  
- **Customization**: Adjust environment variables in your `.env` file to fit your needs.

## Docker Usage

To run these scripts within a Docker container, follow these steps:

1.  **Build the Docker image:**
    ```bash
    docker build -t music-scripts .
    ```

2.  **Run the Docker container:**
    ```bash
    docker run -it --rm -v "$(pwd)":/app --env-file .env music-scripts
    ```
    - `-it`: Runs the container in interactive mode with a terminal.
    - `--rm`: Automatically removes the container when it exits.
    - `-v "$(pwd)":/app`: Mounts the current directory into the `/app` directory in the container. This allows you to edit files locally and have the changes reflected in the container.
    - `--env-file .env`: Loads environment variables from a `.env` file.

3.  **Using the scripts:**
    Once inside the container, you can run the scripts as you would locally:
    ```bash
    python3 loader.py --id 12345 --type artist
    python3 matcher.py --youtube
    python3 builder.py --mode navidrome
    ```