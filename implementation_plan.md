# Implementation Plan - Top 5 Video Processor

## Goal
Modify `process_videos.py` to create a "Top 5" compilation video. The videos should be played in reverse order (Rank 5 to Rank 1), with a cumulative text overlay showing the rankings and the current video's Original Poster (OP).

## User Review Required
> [!IMPORTANT]
> **FFmpeg Complexity**: The script will generate a very long and complex FFmpeg command. This might hit command-line length limits on Windows if the paths or titles are very long. I will try to keep paths relative or short.

> [!NOTE]
> **Font**: The script assumes `arial.ttf` is available. On Windows, we might need to point to `C:\Windows\Fonts\arial.ttf` or assume it's in the current directory.

## Proposed Changes

### `process_videos.py`

#### [MODIFY] `process_videos.py`
- **Filename Parsing**: Add logic to parse `[N]__[OP]__[Title].ext` filenames.
- **Sorting**: Sort files by the index `[N]`.
- **Reverse Processing**: Iterate through the sorted list in reverse (5, 4, 3, 2, 1).
- **Text Overlay Logic**:
    - Define colors:
        - Rank 1: Gold (`#FFD700`)
        - Rank 2: Silver (`#C0C0C0`)
        - Rank 3: Bronze (`#CD7F32`)
        - Rank 4-5: Dark Purple (`#301934`)
        - OP: Neon Blue (`#1F51FF`)
    - For each video segment:
        - Build the text string for lines 1-5.
            - If the rank is "revealed" (i.e., we are at that video or a later one in the sequence), show the title.
            - Otherwise, leave empty.
        - Build the OP text string.
- **FFmpeg Filter Graph**:
    - Instead of `concat` demuxer (text file), use `filter_complex`.
    - Chain: `[0:v]drawtext...[v0]; [1:v]drawtext...[v1]; ... [v0][0:a][v1][1:a]...concat...`
    - Handle audio mapping safely (if audio is missing, generate silence? Or assume all have audio). *Assumption: All downloaded videos have audio or we accept silence if missing.*

## Verification Plan

### Automated Tests
- Create 5 dummy video files with the correct naming convention in a test folder.
- Run `process_videos.py`.
- Check if `output.mp4` is generated.
- (Manual) Watch the video to verify:
    - Order is 5 -> 1.
    - Text appears cumulatively.
    - Colors are correct.
    - OP updates correctly.
