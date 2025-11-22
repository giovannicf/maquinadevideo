import os
import shutil
import math
import subprocess

def get_aspect_ratio(video_path):
    """
    Detects the aspect ratio of a video file using ffprobe.
    Returns 'vertical' if height > width, 'horizontal' if width >= height, or None if detection fails.
    """
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=width,height",
            "-of", "csv=p=0",
            video_path
        ]
        output = subprocess.check_output(cmd).decode("utf-8").strip()
        
        if output:
            width, height = map(int, output.split(','))
            return 'vertical' if height > width else 'horizontal'
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError) as e:
        print(f"  Warning: Could not detect aspect ratio for {os.path.basename(video_path)}: {e}")
        return None
    
    return None

def add_rank_to_filenames(folder_path, video_extensions=('.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv')):
    """
    Adds rank numbers to filenames in the format [N]__[ID]__[OP]__[Title].ext
    Expects input format: [ID]__[OP]__[Title].ext
    """
    files = [f for f in os.listdir(folder_path) if f.lower().endswith(video_extensions)]
    
    # Filter files that don't already have rank numbers (format: [ID]__[OP]__[Title].ext)
    # Files with rank numbers start with a digit followed by __
    files_to_rank = []
    for f in files:
        parts = f.split("__")
        # If first part is numeric and there are only 3 parts, it already has a rank
        if len(parts) >= 3:
            try:
                int(parts[0])
                # Already has rank number, skip
                continue
            except ValueError:
                # First part is not numeric (it's the ID), needs ranking
                files_to_rank.append(f)
        else:
            # Doesn't match expected format, skip
            continue
    
    if not files_to_rank:
        return
    
    # Sort files alphabetically for consistent ranking
    files_to_rank.sort()
    
    print(f"Adding rank numbers to {len(files_to_rank)} files in {os.path.basename(folder_path)}...")
    
    for rank, filename in enumerate(files_to_rank, start=1):
        old_path = os.path.join(folder_path, filename)
        new_filename = f"{rank}__{filename}"
        new_path = os.path.join(folder_path, new_filename)
        
        try:
            os.rename(old_path, new_path)
            print(f"  Ranked: {filename} -> {new_filename}")
        except OSError as e:
            print(f"  Error ranking {filename}: {e}")


def organize_downloads(base_dir="downloads", max_files_per_folder=5):
    """
    Scans subfolders in base_dir. Detects aspect ratio of each video and organizes them into
    separate folders: folder_v_part1, folder_v_part2 for vertical videos and
    folder_h_part1, folder_h_part2 for horizontal videos.
    The original files remain in the source folder as a repository.
    """
    if not os.path.exists(base_dir):
        print(f"Directory '{base_dir}' does not exist.")
        return

    # Get list of immediate subfolders
    subfolders = [f.path for f in os.scandir(base_dir) if f.is_dir()]

    for folder_path in subfolders:
        folder_name = os.path.basename(folder_path)
        
        # First, add rank numbers to files that don't have them yet
        # This transforms [ID]__[OP]__[Title].ext to [N]__[ID]__[OP]__[Title].ext
        add_rank_to_filenames(folder_path)
        
        # Skip folders that are already "parts" (end with _v_partN or _h_partN)
        if any(folder_name.endswith(f"{orient}_part{i}") for orient in ['_v', '_h'] for i in range(1, 100)):
            print(f"Skipping '{folder_name}' (already a part folder)")
            continue
        
        video_extensions = ('.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv')
        
        # Get all video files in the folder, sorted by name
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(video_extensions)]
        files.sort()  # Sort to ensure deterministic order
        
        total_files = len(files)
        
        if total_files == 0:
            print(f"'{folder_name}': No video files found")
            continue
            
        print(f"'{folder_name}': {total_files} files - detecting aspect ratios and organizing...")
        
        # Classify files by aspect ratio
        vertical_files = []
        horizontal_files = []
        
        for filename in files:
            file_path = os.path.join(folder_path, filename)
            aspect_ratio = get_aspect_ratio(file_path)
            
            if aspect_ratio == 'vertical':
                vertical_files.append(filename)
            elif aspect_ratio == 'horizontal':
                horizontal_files.append(filename)
            else:
                # If detection fails, default to horizontal
                print(f"  Defaulting to horizontal for: {filename}")
                horizontal_files.append(filename)
        
        print(f"  Found {len(vertical_files)} vertical and {len(horizontal_files)} horizontal videos")
        
        # Organize vertical files
        if vertical_files:
            organize_by_orientation(base_dir, folder_name, folder_path, vertical_files, 
                                   'v', max_files_per_folder, video_extensions)
        
        # Organize horizontal files
        if horizontal_files:
            organize_by_orientation(base_dir, folder_name, folder_path, horizontal_files, 
                                   'h', max_files_per_folder, video_extensions)


def organize_by_orientation(base_dir, folder_name, source_folder, files, orientation, 
                            max_files_per_folder, video_extensions):
    """
    Helper function to organize files of a specific orientation into part folders.
    orientation: 'v' for vertical, 'h' for horizontal
    """
    current_part = 1
    current_file_index = 0
    total_files = len(files)
    
    while current_file_index < total_files:
        # Construct target folder name: folder_v_part1, folder_h_part2, etc.
        target_folder_name = f"{folder_name}_{orientation}_part{current_part}"
        target_folder_path = os.path.join(base_dir, target_folder_name)
        
        if not os.path.exists(target_folder_path):
            os.makedirs(target_folder_path)
            print(f"  Created: {target_folder_name}")
            
        # Count existing files in target (in case it already has some)
        existing_files = [f for f in os.listdir(target_folder_path) if f.lower().endswith(video_extensions)]
        space_available = max_files_per_folder - len(existing_files)
        
        if space_available <= 0:
            # Target is full, try next part
            current_part += 1
            continue
            
        # Copy files
        chunk = files[current_file_index : current_file_index + space_available]
        
        for file_to_copy in chunk:
            src = os.path.join(source_folder, file_to_copy)
            dst = os.path.join(target_folder_path, file_to_copy)
            try:
                shutil.copy2(src, dst)
                print(f"  Copied: {file_to_copy} -> {target_folder_name}")
            except Exception as e:
                print(f"  Error copying {file_to_copy}: {e}")
        
        current_file_index += len(chunk)
        
        # If we filled this folder, move to next part for the remaining files
        if len(chunk) == space_available:
            current_part += 1

if __name__ == "__main__":
    print("Starting organization...")
    organize_downloads()
    print("Organization complete.")
