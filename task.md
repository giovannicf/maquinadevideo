# Reddit Video Downloader Project

- [x] Verify FFmpeg installation and functionality
- [x] Implement `reddit-downloader.py`
    - [x] Basic download functionality
    - [x] Add `--images` flag (toggle between `yt-dlp` and `gallery-dl`)
    - [x] Add `--downloader` flag
    - [x] Implement `downloads/` subfolder structure
    - [x] Implement custom filename format: `[N]__[OP]__[CleanedName].mp4`
        - [x] `yt-dlp` implementation
        - [x] `gallery-dl` implementation (post-processing)
- [x] Create `organizer.py` script
    - [x] Limit folders to 5 videos
    - [x] Handle overflow with `_partN` folders
- [x] Refactor `process_videos.py` to use system FFmpeg
    - [x] Implement Top 5 ranking logic (reverse order, cumulative text)
    - [x] Handle missing audio (silence generation)
    - [x] Handle resolution mismatch (scale/pad to 1080p)
    - [x] Save output to source folder
- [ ] Create `process_videos.md` documentation <!-- id: 0 -->
