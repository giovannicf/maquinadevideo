
import os
import subprocess

def process_videos(video_folder="video1", logo_path="logo.png", output_filename="output.mp4"):
    video_files = []
    for f in os.listdir(video_folder):
        if f.endswith((".mp4", ".avi", ".mov", ".mkv")):  # Add other video extensions if needed
            video_files.append(os.path.join(video_folder, f))

    if not video_files:
        print(f"Nenhum arquivo de vídeo encontrado na pasta: {video_folder}")
        return

    # Create mylist.txt for ffmpeg concatenation
    with open("mylist.txt", "w") as f:
        for video_file in video_files:
            f.write(f"file '{video_file}'\n")

    # FFmpeg command for concatenation, logo watermark, and text watermark
    # The logo.png is assumed to be in the current directory.
    # Text "teste" in blue, Arial Bold, bottom center.
    # Logo in top center.

    ffmpeg_command = [
        r"C:\harley\pes\ffmpeg\bin\ffmpeg.exe",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", "mylist.txt",
        "-i", logo_path,  # Input for logo
        "-filter_complex",
        "[0:v]scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2,setsar=1[v0];\n[v0]drawtext=text='teste':fontfile=arial.ttf:fontcolor=blue:fontsize=50:x=(w-text_w)/2:y=h-th-20:fix_bounds=true:box=0:boxcolor=white@0.0[v1];\n[1:v]scale=iw/2:ih/2[logo_scaled];\n[v1][logo_scaled]overlay=(W-w)/2:20[outv]",
        "-map", "[outv]",
        "-map", "0:a?",  # Map audio if it exists
        "-c:v", "libx264",
        "-preset", "medium",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        output_filename
    ]

    print("Executando comando FFmpeg:")
    print(" ".join(ffmpeg_command))

    try:
        subprocess.run(ffmpeg_command, check=True)
        print(f"Vídeo processado com sucesso: {output_filename}")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar FFmpeg: {e}")
        print(f"Stderr: {e.stderr}")
    except FileNotFoundError:
        print("Erro: FFmpeg não encontrado. Certifique-se de que está instalado e no PATH.")

if __name__ == "__main__":
    process_videos(output_filename="video1/video1.mp4")
