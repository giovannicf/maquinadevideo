import os
import shutil
import math

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
    Scans subfolders in base_dir. If a folder has more than max_files_per_folder videos,
    it copies files to new folders named folder_part1, folder_part2, folder_part3, etc.
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
        
        # Skip folders that are already "parts" (end with _partN) to avoid re-organizing parts
        if folder_name.endswith(tuple(f"_part{i}" for i in range(1, 100))):
            print(f"Skipping '{folder_name}' (already a part folder)")
            continue
        
        video_extensions = ('.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv')
        
        # Get all video files in the folder, sorted by name (or creation time? Name is usually safer for stability)
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(video_extensions)]
        files.sort() # Sort to ensure deterministic order
        
        total_files = len(files)
        
        if total_files == 0:
            print(f"'{folder_name}': No video files found")
            continue
            
        print(f"'{folder_name}': {total_files} files - organizing into parts...")
        
        # Copy all files to part folders
        # We'll create folder_part1, folder_part2, etc.
        # Each part folder gets max_files_per_folder files
        
        current_part = 1
        current_file_index = 0
        
        while current_file_index < total_files:
            # Logic:
            # 1. Construct target folder name: "{folder_name}_part{current_part}"
            # 2. Create it if not exists.
            # 3. Check how many files are in it.
            # 4. Copy files until it has max_files_per_folder.
            # 5. Increment part number.
            
            target_folder_name = f"{folder_name}_part{current_part}"
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
                src = os.path.join(folder_path, file_to_copy)
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
