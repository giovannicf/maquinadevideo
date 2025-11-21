import os
import shutil
import math

def organize_downloads(base_dir="downloads", max_files_per_folder=5):
    """
    Scans subfolders in base_dir. If a folder has more than max_files_per_folder videos,
    it moves the excess files to new folders named folder_part2, folder_part3, etc.
    """
    if not os.path.exists(base_dir):
        print(f"Directory '{base_dir}' does not exist.")
        return

    # Get list of immediate subfolders
    subfolders = [f.path for f in os.scandir(base_dir) if f.is_dir()]

    for folder_path in subfolders:
        folder_name = os.path.basename(folder_path)
        
        # Skip folders that are already "parts" (end with _partN) to avoid infinite loops or re-organizing parts
        # actually, we should probably process them too if they got overfilled, but for now let's focus on the main ones
        # or better: treat "folder_part2" as just another folder. 
        # BUT, the requirement implies splitting a big folder into parts.
        # If we have "myfolder" with 15 files.
        # We want: "myfolder" (5), "myfolder_part2" (5), "myfolder_part3" (5).
        
        video_extensions = ('.mp4', '.mkv', '.webm', '.mov', '.avi', '.flv')
        
        # Get all video files in the folder, sorted by name (or creation time? Name is usually safer for stability)
        files = [f for f in os.listdir(folder_path) if f.lower().endswith(video_extensions)]
        files.sort() # Sort to ensure deterministic order
        
        total_files = len(files)
        
        if total_files <= max_files_per_folder:
            print(f"'{folder_name}': {total_files} files (OK)")
            continue
            
        print(f"'{folder_name}': {total_files} files (Exceeds limit of {max_files_per_folder})")
        
        # Calculate how many extra parts we need
        # We keep the first 'max_files_per_folder' in the original folder
        # The rest need to be moved.
        
        files_to_move = files[max_files_per_folder:]
        
        # We need to find the next available part number.
        # If "folder_part2" exists, we check "folder_part3", etc.
        
        # Base name for parts. If the current folder is ALREADY a part (e.g. "foo_part2"),
        # we should probably treat it as a source? 
        # The user prompt says: "create a new folder with the name of the folder... followed by _part[n]"
        # So if "foo" has 12 files -> "foo" (5), "foo_part2" (5), "foo_part3" (2).
        
        # What if "foo_part2" already exists? We should append to it or skip to part3?
        # Let's assume we fill sequentially.
        
        current_part = 2
        current_file_index = 0
        
        while current_file_index < len(files_to_move):
            # Determine target folder name
            # Check if the current folder name already ends with _part\d+
            # If so, we might want to increment THAT number? 
            # But the simplest interpretation is: Source is "folder". Targets are "folder_part2", "folder_part3".
            
            # Logic:
            # 1. Construct target folder name: "{folder_name}_part{current_part}"
            # 2. Create it if not exists.
            # 3. Check how many files are in it.
            # 4. Move files until it has 5.
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
                
            # Move files
            chunk = files_to_move[current_file_index : current_file_index + space_available]
            
            for file_to_move in chunk:
                src = os.path.join(folder_path, file_to_move)
                dst = os.path.join(target_folder_path, file_to_move)
                try:
                    shutil.move(src, dst)
                    print(f"  Moved: {file_to_move} -> {target_folder_name}")
                except Exception as e:
                    print(f"  Error moving {file_to_move}: {e}")
            
            current_file_index += len(chunk)
            
            # If we filled this folder, move to next part for the remaining files
            if len(chunk) == space_available:
                current_part += 1

if __name__ == "__main__":
    print("Starting organization...")
    organize_downloads()
    print("Organization complete.")
