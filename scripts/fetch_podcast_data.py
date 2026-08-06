#!/usr/bin/env python3
"""
Podcast Data Extractor & Local Transcriber using yt-dlp, Buzz CLI, and GraphifyMapper.
Supports Siemens.FM, Spotify, Apple Podcasts, YouTube audio, direct .mp3/.m4a links, and RSS feeds.
"""

import os
import sys
import json
import argparse
import subprocess
import re
from pathlib import Path
from typing import Dict, Any, Optional

PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR))

from scripts.graphify_mapper import map_context_with_graphify

TEMP_DIR = PROJECT_DIR / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)

def download_audio_with_ytdlp(url: str, output_mp3_path: Path) -> bool:
    """Download audio track from URL using yt-dlp."""
    print(f"[Podcast Extractor] Downloading audio track via yt-dlp from: {url}", file=sys.stderr)
    cmd = [
        "yt-dlp",
        "--extract-audio",
        "--audio-format", "mp3",
        "--output", str(output_mp3_path.with_suffix("")),
        "--no-playlist",
        url
    ]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if res.returncode == 0 and output_mp3_path.exists():
            return True
        else:
            print(f"[yt-dlp Warning] {res.stderr}", file=sys.stderr)
    except Exception as err:
        print(f"[yt-dlp Error] {err}", file=sys.stderr)
    return False

def download_audio_with_curl(media_url: str, output_mp3_path: Path) -> bool:
    """Fallback: direct download media file using curl."""
    print(f"[Podcast Extractor] Fallback download media via curl: {media_url}", file=sys.stderr)
    cmd = ["curl", "-sSL", media_url, "-o", str(output_mp3_path)]
    try:
        res = subprocess.run(cmd, capture_output=True, timeout=120)
        if res.returncode == 0 and output_mp3_path.exists() and output_mp3_path.stat().st_size > 1000:
            return True
    except Exception as err:
        print(f"[curl Error] {err}", file=sys.stderr)
    return False

def transcribe_audio_with_buzz(mp3_path: Path) -> str:
    """Transcribe audio using local Buzz CLI (Whisper model)."""
    buzz_bin = "/Applications/Buzz.app/Contents/MacOS/Buzz"
    if not Path(buzz_bin).exists():
        raise RuntimeError("Buzz CLI binary not found at /Applications/Buzz.app/Contents/MacOS/Buzz")

    print(f"[Podcast Extractor] Running Buzz CLI transcription on {mp3_path.name}...", file=sys.stderr)
    cmd = [
        buzz_bin,
        "add", "--txt", "--hide-gui",
        "-s", "tiny", "-l", "en",
        "-d", str(TEMP_DIR),
        str(mp3_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True, timeout=600)

    # Find the generated txt file in TEMP_DIR excluding fetched_data.txt
    txt_files = [p for p in TEMP_DIR.glob("*.txt") if p.name not in ("fetched_data.txt", "fetched_book_data.txt")]
    if txt_files:
        transcription_txt = sorted(txt_files, key=lambda p: p.stat().st_mtime, reverse=True)[0]
        text_content = transcription_txt.read_text(encoding="utf-8")
        try:
            if transcription_txt.name not in ("fetched_data.txt", "fetched_book_data.txt"):
                transcription_txt.unlink()
        except Exception:
            pass
        return text_content
    
    raise RuntimeError("No transcription text file produced by Buzz CLI.")

def extract_podcast_episode(url: str) -> Dict[str, Any]:
    """Fetch, download audio, transcribe, and map context for a podcast episode."""
    mp3_target = TEMP_DIR / "podcast_audio.mp3"
    if mp3_target.exists():
        mp3_target.unlink()

    # Step 1: Download audio
    downloaded = download_audio_with_ytdlp(url, mp3_target)
    if not downloaded:
        # Try extracting direct media URL if passed as query or og:audio
        downloaded = download_audio_with_curl(url, mp3_target)

    if not downloaded:
        raise RuntimeError(f"Could not download audio from URL: {url}")

    # Step 2: Transcribe via Buzz CLI
    transcript_text = transcribe_audio_with_buzz(mp3_target)

    # Clean up mp3 after transcription
    if mp3_target.exists():
        try:
            mp3_target.unlink()
        except Exception:
            pass

    # Extract metadata title snippet
    snippet_lines = [line.strip() for line in transcript_text.splitlines() if line.strip()]
    title = f"Podcast Episode — {snippet_lines[0][:60]}" if snippet_lines else "Podcast Episode"
    snippet = " ".join(snippet_lines[:10])

    # Step 3: Enriched Graphify Context
    graphify_ctx = map_context_with_graphify(title, snippet)

    payload = {
        "url": url,
        "metadata": {
            "title": title,
            "channel": "Podcast / Audio",
            "date": "August 2026",
            "url": url,
            "type": "podcast"
        },
        "graphify_context": graphify_ctx
    }

    # Save to temp/fetched_data.json and temp/fetched_data.txt
    json_path = TEMP_DIR / "fetched_data.json"
    txt_path = TEMP_DIR / "fetched_data.txt"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    txt_path.write_text(transcript_text, encoding="utf-8")

    print(f"[Podcast Extractor] Successfully ingested and saved to {json_path} and {txt_path}", file=sys.stderr)
    return payload

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch and transcribe podcast audio")
    parser.add_argument("--url", required=True, help="Podcast or audio URL")
    args = parser.parse_args()

    result = extract_podcast_episode(args.url)
    print(json.dumps(result, indent=2, ensure_ascii=False))
