#!/usr/bin/env python3
"""
ytdlp_mcp — MCP server (stdio) to download YouTube transcripts via yt-dlp.

Tools:
  - ytdlp_get_transcript        → transcript of an individual video
  - ytdlp_get_playlist          → transcripts of an entire playlist
  - ytdlp_list_playlist_videos  → lists the videos of a playlist without downloading
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP("ytdlp_mcp")

YTDLP_BIN = "yt-dlp" # Updated to use version from PATH or UV environment

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_vtt(vtt_content: str) -> str:
    """Converts a VTT file to clean and deduplicated plain text."""
    content = re.sub(r'WEBVTT\n.*?\n\n', '', vtt_content, flags=re.DOTALL)
    content = re.sub(
        r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}[^\n]*\n',
        '', content
    )
    content = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
    lines = content.split('\n')
    seen, unique = set(), []
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            unique.append(line)
    return ' '.join(unique)


def _run_ytdlp_subtitles(url: str, lang: str, output_dir: Path) -> dict:
    """
    Runs yt-dlp to download subtitles.
    Returns dict: {video_id: {title, url, transcript, lang_found}}
    """
    cmd = [
        YTDLP_BIN,
        '--write-auto-sub',
        '--write-sub',
        '--sub-lang', lang,
        '--sub-format', 'vtt',
        '--skip-download',
        '--no-playlist-reverse',
        '--print', '%(id)s|||%(title)s|||%(webpage_url)s',
        '--output', str(output_dir / '%(playlist_index)s-%(id)s.%(ext)s'),
        url
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(output_dir), timeout=120
    )

    # Parse video info from stdout
    videos = {}
    for line in result.stdout.strip().split('\n'):
        if '|||' in line:
            parts = line.split('|||')
            if len(parts) >= 2:
                vid_id = parts[0].strip()
                title = parts[1].strip()
                vid_url = parts[2].strip() if len(parts) > 2 else ''
                videos[vid_id] = {
                    'title': title,
                    'url': vid_url,
                    'transcript': '',
                    'lang_found': None,
                    'error': None
                }

    if not videos and result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr[:300]}")

    # Read generated VTT files and assign to each video
    for vtt_file in output_dir.glob('*.vtt'):
        try:
            content = vtt_file.read_text(encoding='utf-8')
            clean = _clean_vtt(content)
            stem = vtt_file.stem  # e.g. "1-KSItlTAsMsk.en"
            # Detect lang from file name
            lang_found = stem.split('.')[-1] if '.' in stem else lang
            # Find which video it belongs to
            for vid_id in videos:
                if vid_id in stem:
                    videos[vid_id]['transcript'] = clean
                    videos[vid_id]['lang_found'] = lang_found
                    break
        except Exception as e:
            continue

    # Mark videos without transcripts
    for vid_id, info in videos.items():
        if not info['transcript']:
            info['error'] = 'Transcript not available (video without subtitles or private)'

    return videos


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class TranscriptInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    url: str = Field(
        ...,
        description="YouTube video URL. E.g. https://www.youtube.com/watch?v=KSItlTAsMsk",
        min_length=10
    )
    lang: str = Field(
        default='en',
        description="Subtitle language code. E.g. 'en', 'es', 'fr'. Default: 'en'",
        min_length=2,
        max_length=10
    )


class PlaylistInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    url: str = Field(
        ...,
        description="YouTube playlist URL. E.g. https://www.youtube.com/playlist?list=PL...",
        min_length=10
    )
    lang: str = Field(
        default='en',
        description="Subtitle language code. Default: 'en'",
        min_length=2,
        max_length=10
    )
    max_videos: Optional[int] = Field(
        default=None,
        description="Maximum number of videos to process. None = all. Useful for large playlists.",
        ge=1,
        le=200
    )


class ListPlaylistInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    url: str = Field(
        ...,
        description="YouTube playlist URL.",
        min_length=10
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    name="ytdlp_get_transcript",
    annotations={
        "title": "Get transcript for a YouTube video",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def ytdlp_get_transcript(params: TranscriptInput) -> str:
    """
    Downloads and returns the transcript (subtitles) of a YouTube video.

    Uses yt-dlp to download auto-generated or manual subtitles in the specified
    language, cleans the VTT formatting, and returns plain text ready for processing.

    Args:
        params (TranscriptInput):
            - url (str): YouTube video URL
            - lang (str): Subtitle language code ('en', 'es', 'fr'...). Default: 'en'

    Returns:
        str: JSON with:
            - video_id (str): Video ID
            - title (str): Video title
            - url (str): Video URL
            - lang (str): Found language
            - transcript (str): Full clean transcript text
            - error (str|null): Error message if no transcript is available
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        try:
            videos = _run_ytdlp_subtitles(params.url, params.lang, tmp_path)
        except RuntimeError as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)

        if not videos:
            return json.dumps(
                {"error": f"No video found at: {params.url}"},
                ensure_ascii=False, indent=2
            )

        # For a single video, return the first one
        vid_id, info = next(iter(videos.items()))
        result = {
            "video_id": vid_id,
            "title": info['title'],
            "url": info['url'],
            "lang": info.get('lang_found') or params.lang,
            "transcript": info['transcript'],
            "char_count": len(info['transcript']),
            "error": info.get('error')
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool(
    name="ytdlp_get_playlist",
    annotations={
        "title": "Get transcripts of a complete YouTube playlist",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def ytdlp_get_playlist(params: PlaylistInput) -> str:
    """
    Downloads and returns the transcripts of all videos in a YouTube playlist.

    Processes each video in the playlist in order, downloading their auto-generated
    or manual subtitles. Ideal for processing complete courses, series, or video collections.

    Args:
        params (PlaylistInput):
            - url (str): YouTube playlist URL
            - lang (str): Language code. Default: 'en'
            - max_videos (int|None): Limit of videos to process. None = all.

    Returns:
        str: JSON with:
            - playlist_url (str): Processed playlist URL
            - total_videos (int): Total processed videos
            - lang (str): Requested language
            - videos (list): List of objects with video_id, title, url, transcript, error
            - summary (dict): Statistics: total, with_transcript, without_transcript
    """
    # Apply limit if specified
    url = params.url
    if params.max_videos:
        # yt-dlp accepts --playlist-end to limit
        cmd_extra = ['--playlist-end', str(params.max_videos)]
    else:
        cmd_extra = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        try:
            if cmd_extra:
                # Inject extra flags before the URL
                import shlex
                # Use direct subprocess to pass additional flags
                cmd = [
                    YTDLP_BIN,
                    '--write-auto-sub', '--write-sub',
                    '--sub-lang', params.lang,
                    '--sub-format', 'vtt',
                    '--skip-download',
                    '--no-playlist-reverse',
                    '--print', '%(id)s|||%(title)s|||%(webpage_url)s',
                    '--output', str(tmp_path / '%(playlist_index)s-%(id)s.%(ext)s'),
                ] + cmd_extra + [url]

                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    cwd=str(tmp_path), timeout=300
                )

                videos = {}
                for line in result.stdout.strip().split('\n'):
                    if '|||' in line:
                        parts = line.split('|||')
                        vid_id = parts[0].strip()
                        title = parts[1].strip() if len(parts) > 1 else ''
                        vid_url = parts[2].strip() if len(parts) > 2 else ''
                        videos[vid_id] = {
                            'title': title, 'url': vid_url,
                            'transcript': '', 'lang_found': None, 'error': None
                        }

                for vtt_file in tmp_path.glob('*.vtt'):
                    try:
                        content = vtt_file.read_text(encoding='utf-8')
                        clean = _clean_vtt(content)
                        stem = vtt_file.stem
                        lang_found = stem.split('.')[-1] if '.' in stem else params.lang
                        for vid_id in videos:
                            if vid_id in stem:
                                videos[vid_id]['transcript'] = clean
                                videos[vid_id]['lang_found'] = lang_found
                                break
                    except Exception:
                        continue

                for vid_id, info in videos.items():
                    if not info['transcript']:
                        info['error'] = 'Transcript not available'
            else:
                videos = _run_ytdlp_subtitles(url, params.lang, tmp_path)

        except RuntimeError as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)

        video_list = []
        for vid_id, info in videos.items():
            video_list.append({
                "video_id": vid_id,
                "title": info['title'],
                "url": info['url'],
                "lang": info.get('lang_found') or params.lang,
                "transcript": info['transcript'],
                "char_count": len(info['transcript']),
                "error": info.get('error')
            })

        con_transcript = sum(1 for v in video_list if v['transcript'])
        sin_transcript = len(video_list) - con_transcript

        response = {
            "playlist_url": url,
            "total_videos": len(video_list),
            "lang": params.lang,
            "videos": video_list,
            "summary": {
                "total": len(video_list),
                "con_transcript": con_transcript,
                "sin_transcript": sin_transcript
            }
        }
        return json.dumps(response, ensure_ascii=False, indent=2)


@mcp.tool(
    name="ytdlp_list_playlist_videos",
    annotations={
        "title": "List videos in a playlist without downloading transcripts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def ytdlp_list_playlist_videos(params: ListPlaylistInput) -> str:
    """
    Lists the videos of a YouTube playlist without downloading subtitles.

    Useful for exploring a playlist's content before deciding which videos
    to process with ytdlp_get_transcript or ytdlp_get_playlist.

    Args:
        params (ListPlaylistInput):
            - url (str): YouTube playlist URL

    Returns:
        str: JSON with:
            - playlist_url (str): Playlist URL
            - total_videos (int): Total number of videos
            - videos (list): List with index, video_id, title, url for each video
    """
    cmd = [
        YTDLP_BIN,
        '--flat-playlist',
        '--print', '%(playlist_index)s|||%(id)s|||%(title)s|||%(webpage_url)s',
        params.url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0 and not result.stdout:
        return json.dumps(
            {"error": f"Error listing playlist: {result.stderr[:300]}"},
            ensure_ascii=False, indent=2
        )

    videos = []
    for line in result.stdout.strip().split('\n'):
        if '|||' in line:
            parts = line.split('|||')
            if len(parts) >= 3:
                videos.append({
                    "index": parts[0].strip(),
                    "video_id": parts[1].strip(),
                    "title": parts[2].strip(),
                    "url": parts[3].strip() if len(parts) > 3 else f"https://youtu.be/{parts[1].strip()}"
                })

    return json.dumps({
        "playlist_url": params.url,
        "total_videos": len(videos),
        "videos": videos
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()  # stdio transport by default
