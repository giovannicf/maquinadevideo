import argparse
import os
import subprocess
import sys
import re

# Archive filename for tracking downloaded Reddit post IDs
ARCHIVE_FILENAME = ".downloaded_ids.txt"



def download_reddit_videos(url, folder, download_images=False, downloader="yt-dlp"):
    """
    Downloads videos (and optionally images) from a Reddit URL to a specified folder.
    
    Args:
        url (str): The Reddit URL.
        folder (str): The output subfolder name (will be created inside 'downloads/').
        download_images (bool): If True, download images and videos.
        downloader (str): The tool to use ('yt-dlp' or 'gallery-dl').
    """
    # Define the base downloads directory
    base_dir = "downloads"
    # Construct the full path
    full_path = os.path.join(base_dir, folder)

    # Create the folder if it doesn't exist
    if not os.path.exists(full_path):
        try:
            os.makedirs(full_path)
            print(f"Created directory: {full_path}")
        except OSError as e:
            print(f"Error creating directory {full_path}: {e}")
            sys.exit(1)

    # Add ffmpeg to PATH
    ffmpeg_path = r"C:\harley\pes\ffmpeg\bin"
    os.environ["PATH"] = ffmpeg_path + os.pathsep + os.environ["PATH"]
    
    # Archive file path for duplicate detection
    archive_path = os.path.join(full_path, ARCHIVE_FILENAME)

    command = []
    
    if downloader == "gallery-dl":
        print(f"Using gallery-dl...")
        # Use --filename to set the format: [ID]__[OP]__[CleanedName].ext
        # {id}: Reddit post ID
        # {author}: OP
        # {title}: Title
        command = [
            sys.executable, "-m", "gallery_dl",
            "--directory", full_path,
            "--filename", "{id}__{author}__{title}.{extension}",
            "--download-archive", archive_path,
            url
        ]
        
        if not download_images:
            print("Image download DISABLED. Filtering out image extensions...")
            # Filter out common image extensions
            command.extend(["--filter", "extension not in ('jpg', 'jpeg', 'png', 'gif', 'webp')"])
        else:
            print("Image download ENABLED.")

    else: # downloader == "yt-dlp"
        print(f"Using yt-dlp...")
        # yt-dlp defaults to videos. 
        # If user wanted images with yt-dlp, it's not really supported well, so we just run it.
        if download_images:
             print("Warning: yt-dlp is primarily for videos. Some images might not be downloaded.")
        
        # Construct the output template: [ID]__[OP]__[CleanedName].ext
        # %(id)s: Reddit post ID
        # %(uploader)s: Original Poster (OP)
        # %(title)s: Title (will be cleaned by --replace-in-metadata)
        output_template = "%(id)s__%(uploader)s__%(title)s.%(ext)s"

        # -o specifies the output template inside the folder
        # --paths specifies the download directory
        # --replace-in-metadata: Cleans the title by removing non-alphanumeric characters (keeping underscores)
        # --download-archive: Track downloaded IDs to prevent duplicates
        command = [
            sys.executable, "-m", "yt_dlp",
            "--paths", full_path,
            "-o", output_template,
            "--replace-in-metadata", "title", "[^a-zA-Z0-9_]", "",
            "--download-archive", archive_path,
            url
        ]

    print(f"Downloading from {url} to {full_path}...")
    print(f"Command: {' '.join(command)}")

    try:
        subprocess.run(command, check=True)
        print("Download completed successfully.")
        print(f"Archive file updated: {archive_path}")
            
    except subprocess.CalledProcessError as e:
        print(f"Error occurred during download: {e}")
        # Don't exit immediately if it's just a "no video found" error from yt-dlp, 
        # but usually check=True raises the error.
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download videos from Reddit.")
    parser.add_argument("url", help="The Reddit URL to download from.")
    parser.add_argument("folder", help="The subfolder name to save the downloaded videos (inside 'downloads/').")
    parser.add_argument("--images", action="store_true", help="Enable image downloading. Default is False (videos only).")
    parser.add_argument("--downloader", choices=["yt-dlp", "gallery-dl"], default="yt-dlp", help="Choose the downloader tool. Default is yt-dlp.")

    args = parser.parse_args()

    download_reddit_videos(args.url, args.folder, args.images, args.downloader)
