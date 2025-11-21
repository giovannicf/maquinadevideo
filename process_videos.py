
import os
import subprocess
import re
import sys

def parse_filename(filename):
    """
    Parses filename in format [N]__[OP]__[Title].ext
    Returns (index, op, title) or None if not matching.
    """
    # Remove extension
    name, ext = os.path.splitext(filename)
    parts = name.split("__")
    if len(parts) >= 3:
        try:
            index = int(parts[0])
            op = parts[1]
            title = "__".join(parts[2:]) # Rejoin title if it had underscores
            return index, op, title
        except ValueError:
            pass
    return None

def has_audio(filename):
    """Checks if the video file has an audio stream."""
    try:
        cmd = [
            "ffprobe", 
            "-v", "error", 
            "-select_streams", "a", 
            "-show_entries", "stream=codec_type", 
            "-of", "csv=p=0", 
            filename
        ]
        output = subprocess.check_output(cmd).decode("utf-8").strip()
        return len(output) > 0
    except subprocess.CalledProcessError:
        return False

def get_video_duration(filename):
    """Gets the duration of a video file in seconds."""
    try:
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "csv=p=0",
            filename
        ]
        output = subprocess.check_output(cmd).decode("utf-8").strip()
        return float(output)
    except (subprocess.CalledProcessError, ValueError):
        return 0.0

def process_videos(video_folder, output_filename="final_video.mp4", aspect_ratio="vertical", logo_path="logo.png"):
    # Validate aspect ratio parameter
    if aspect_ratio not in ["vertical", "horizontal"]:
        print(f"Invalid aspect_ratio: {aspect_ratio}. Must be 'vertical' or 'horizontal'. Defaulting to 'vertical'.")
        aspect_ratio = "vertical"
    
    # Set target resolution based on aspect ratio
    if aspect_ratio == "vertical":
        target_width = 1080
        target_height = 1920
    else:  # horizontal
        target_width = 1920
        target_height = 1080
    
    print(f"Processing videos with {aspect_ratio} aspect ratio ({target_width}x{target_height})")
    
    if not os.path.exists(video_folder):
        print(f"Folder not found: {video_folder}")
        return
        
    # Output path inside the video folder
    output_path = os.path.join(video_folder, output_filename)

    video_extensions = ('.mp4', '.avi', '.mov', '.mkv')
    # Exclude the output file itself if it exists
    files = [f for f in os.listdir(video_folder) if f.lower().endswith(video_extensions) and f != output_filename]
    
    parsed_videos = []
    for f in files:
        parsed = parse_filename(f)
        if parsed:
            parsed_videos.append({'file': f, 'index': parsed[0], 'op': parsed[1], 'title': parsed[2]})
        else:
            print(f"Skipping file (invalid format): {f}")

    # Sort by index (1, 2, 3, 4, 5...)
    parsed_videos.sort(key=lambda x: x['index'])
    
    # Take top 5 (or fewer)
    top_videos = parsed_videos[:5]
    
    if not top_videos:
        print("No valid videos found to process.")
        return

    # We need to process them in REVERSE order (5 -> 1) for the video sequence
    # But the text overlay depends on the "Rank".
    # Rank 1 is the first video in the sorted list.
    # Rank 5 is the 5th video in the sorted list.
    
    # Let's map Rank to Title for the overlay
    # rank_map[1] = Title of video with index 1
    rank_map = {}
    for i, vid in enumerate(top_videos):
        rank = i + 1 # 1-based rank
        rank_map[rank] = vid['title']

    # The playback order is reverse: Rank 5, Rank 4, Rank 3...
    playback_order = list(reversed(top_videos))
    
    # Construct FFmpeg command
    inputs = []
    filter_complex = ""
    
    # Add logo as input if provided
    logo_input_index = None
    if logo_path and os.path.exists(logo_path):
        logo_input_index = len(playback_order)  # Logo will be the last input
        print(f"Adding logo overlay from: {logo_path}")
    
    # Colors
    color_gold = "0xFFD700"
    color_silver = "0xC0C0C0"
    color_bronze = "0xCD7F32"
    color_purple = "0x301934"
    color_neon_blue = "0x1F51FF"
    
    # Font settings
    font_size = 60  # Increased from 40 for better visibility
    line_spacing = 70  # Increased from 50 to accommodate larger text
    start_x = 100  # Left margin increased from 50 to 100 pixels
    start_y = 400  # Moved down from 50 to center text more vertically (for 1920 height)
    
    audio_labels = []
    
    for i, vid in enumerate(playback_order):
        full_path = os.path.join(video_folder, vid['file'])
        inputs.extend(["-i", full_path])
        
        # Check for audio
        if has_audio(full_path):
            audio_labels.append(f"[{i}:a]")
        else:
            # Generate silence with specific duration to match video length
            # This prevents infinite buffering that causes system crashes
            duration = get_video_duration(full_path)
            if duration > 0:
                # Generate silence for the exact duration of the video
                filter_step = f"anullsrc=r=44100:cl=stereo:d={duration}[silence{i}];"
                filter_complex += filter_step
                audio_labels.append(f"[silence{i}]")
            else:
                # Fallback: use a very short silence if duration can't be determined
                filter_step = f"anullsrc=r=44100:cl=stereo:d=0.1[silence{i}];"
                filter_complex += filter_step
                audio_labels.append(f"[silence{i}]")
        
        # Current video's rank in the original sorted list
        # vid['index'] might not be 1..5 if the user downloaded random stuff, 
        # but we sorted them. So let's use their position in top_videos.
        # top_videos[0] is Rank 1.
        # We need to find 'vid' in 'top_videos' to get its Rank.
        current_rank = top_videos.index(vid) + 1
        
        # Build drawtext filters for this video segment
        # We chain them: [v_in]drawtext...[v_mid]; [v_mid]drawtext...[v_out]
        
        chain_in = f"[{i}:v]"
        chain_out = f"v{i}"
        
        # Scale the video to the target resolution based on aspect ratio
        scale_filter = f"{chain_in}scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,setsar=1[scaled{i}];"
        filter_complex += scale_filter
        chain_in = f"[scaled{i}]"
        
        # Simplified: Use input directly (assuming same resolution for now)
        # chain_in is already set to [{i}:v]
        
        # Add text for Ranks 1 to 5
        for r in range(1, 6):
            # Determine color
            if r == 1: color = color_gold
            elif r == 2: color = color_silver
            elif r == 3: color = color_bronze
            else: color = color_purple
            
            # Determine text
            # Show title if the rank is >= current_rank (since we are counting down)
            # Wait.
            # Playback: 5 -> 4 -> 3 -> 2 -> 1
            # When playing 5 (current_rank=5): Show Title 5. 1-4 Empty.
            # When playing 4 (current_rank=4): Show Title 4, Title 5. 1-3 Empty.
            # ...
            # When playing 1 (current_rank=1): Show Title 1, 2, 3, 4, 5.
            
            # So show title if r >= current_rank
            if r >= current_rank and r in rank_map:
                text = f"{r}: {rank_map[r]}"
            else:
                text = f"{r}: "
            
            # Escape text for FFmpeg
            text = text.replace(":", "\\:").replace("'", "").replace("[", "\\[").replace("]", "\\]")
            
            y_pos = start_y + (r - 1) * line_spacing
            
            # Add drawtext filter
            # Using arialbd.ttf for bold text
            
            filter_step = f"{chain_in}drawtext=fontfile='arialbd.ttf':text='{text}':fontcolor={color}:fontsize={font_size}:x={start_x}:y={y_pos}[tmp{i}_{r}];"
            filter_complex += filter_step
            chain_in = f"[tmp{i}_{r}]"

        # Add OP line
        # "OP : @[original poster]"
        op_text = f"OP : @{vid['op']}"
        op_text = op_text.replace(":", "\\:").replace("'", "")
        op_y_pos = start_y + 5 * line_spacing + 70  # Extra spacing (70px instead of 20px) to create empty line effect
        
        filter_step = f"{chain_in}drawtext=fontfile='arialbd.ttf':text='{op_text}':fontcolor={color_neon_blue}:fontsize={font_size}:x={start_x}:y={op_y_pos}[{chain_out}];"
        filter_complex += filter_step
        
    concat_in = ""
    for i in range(len(playback_order)):
        concat_in += f"[v{i}]{audio_labels[i]}"
    
    filter_complex += f"{concat_in}concat=n={len(playback_order)}:v=1:a=1[concatv][outa];"
    
    # Add logo overlay if provided
    if logo_input_index is not None:
        # Display logo at full size (500x500) at top center
        filter_complex += f"[concatv][{logo_input_index}:v]overlay=(W-w)/2:20[outv]"
    else:
        # No logo, just use concat output directly
        filter_complex += f"[concatv]null[outv]"
    
    cmd = ["ffmpeg", "-y"]
    cmd.extend(inputs)
    
    # Add logo input if provided
    if logo_input_index is not None:
        cmd.extend(["-i", logo_path])
    cmd.extend(["-filter_complex", filter_complex, "-map", "[outv]", "-map", "[outa]", output_path])
    
    print("Executing FFmpeg command...")
    # print(" ".join(cmd)) # Debugging
    
    try:
        subprocess.run(cmd, check=True)
        print(f"Video processed successfully: {output_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error running FFmpeg: {e}")

if __name__ == "__main__":
    # Parse command-line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Process and concatenate videos with text overlays")
    parser.add_argument("--folder", default="downloads/test_downloads_part2", help="Folder containing videos to process")
    parser.add_argument("--output", default="final_video.mp4", help="Output filename")
    parser.add_argument("--aspect-ratio", choices=["vertical", "horizontal"], default="vertical", 
                        help="Output video aspect ratio (default: vertical)")
    parser.add_argument("--logo", default="logo.png", help="Path to logo image file (default: logo.png)")
    
    args = parser.parse_args()
    
    process_videos(video_folder=args.folder, output_filename=args.output, aspect_ratio=args.aspect_ratio, logo_path=args.logo)
