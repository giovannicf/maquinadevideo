# Reddit Downloader

A command-line tool to download videos (and optionally images) from Reddit using `yt-dlp` or `gallery-dl`.

## Features

*   **Video Download:** Downloads videos from Reddit posts, subreddits, or user profiles.
*   **Audio/Video Merging:** Automatically merges video and audio streams using FFmpeg.
*   **Image Support:** Optionally downloads images when using `gallery-dl`.
*   **Tool Selection:** Choose between `yt-dlp` (default, robust for videos) and `gallery-dl` (great for mixed media).
*   **Organized Storage:** All downloads are saved in a `downloads/` directory, organized by the subfolder name you provide.

## Prerequisites

1.  **Python 3.x** installed.
2.  **FFmpeg** installed and configured (the script adds `C:\harley\pes\ffmpeg\bin` to PATH automatically).
3.  **Python Packages:**
    *   `yt-dlp`
    *   `gallery-dl`

    Install them via pip:
    ```bash
    pip install yt-dlp gallery-dl
    ```

## Usage

Run the script from the command line:

```bash
python reddit-downloader.py [URL] [FOLDER_NAME] [OPTIONS]
```

### Arguments

*   `url`: The Reddit URL to download from (e.g., a post, subreddit, or user profile).
*   `folder`: The name of the subfolder to save downloads into. This will be created inside the `downloads/` directory.

### Options

*   `--images`: Enable image downloading.
    *   Default: `False` (Videos only).
    *   If used with `gallery-dl`, it downloads images and videos.
    *   If used with `yt-dlp`, it attempts to download images but support is limited.
*   `--downloader {yt-dlp,gallery-dl}`: Choose the downloader tool.
    *   Default: `yt-dlp`.
    *   `yt-dlp`: Best for videos, avoids some rate limits.
    *   `gallery-dl`: Best for galleries and mixed content.

## Examples

**1. Download videos only (Default behavior):**
Uses `yt-dlp` to download videos from a subreddit to `downloads/funny_videos`.
```bash
python reddit-downloader.py https://www.reddit.com/r/funny funny_videos
```

**2. Download videos using gallery-dl:**
Uses `gallery-dl` but filters out images (downloads videos only).
```bash
python reddit-downloader.py https://www.reddit.com/r/funny funny_videos --downloader gallery-dl
```

**3. Download EVERYTHING (Videos + Images):**
Uses `gallery-dl` to download all media types.
```bash
python reddit-downloader.py https://www.reddit.com/r/funny funny_media --downloader gallery-dl --images
```

**4. Download a specific post:**
```bash
python reddit-downloader.py https://www.reddit.com/r/videos/comments/example/video_title/ my_post
```

## Output Structure

Files are saved in:
```
current_directory/
└── downloads/
    └── [FOLDER_NAME]/
        ├── video1.mp4
        ├── image1.jpg
        └── ...
```
