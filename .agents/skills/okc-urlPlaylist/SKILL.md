---
name: okc-urlPlaylist
description: Ingests an entire YouTube playlist, curates each video in order, and syncs the vault.
argument-hint: <url>
---

# YouTube Playlist Curator Skill

When this skill is invoked via `/urlPlaylist <url>`, execute the following steps:

1. **List Playlist Videos:**
   - Fetch the list of all video IDs and titles in the playlist. You can run `ytdlp_list_playlist_videos` or query the YouTube API helper.
2. **Process Each Video sequentially:**
   - For each video in the playlist, in order:
     - Download the transcript (using `youtube-transcript-api` via Python or fallbacks).
     - Generate the curated note in the `raw/` zone.
     - Extract concepts to the `wiki/` zone.
     - Report progress video-by-video to the user.
3. **Synchronize and Verify:**
   - Run the synchronization script:
     ```bash
     uv run python scripts/sync_vault.py
     ```
   - Report the final sync results to the user.
