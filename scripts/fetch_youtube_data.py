#!/usr/bin/env python3
import os
import sys
import re
import argparse
import subprocess
import json
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi

PROJECT_DIR = Path(__file__).parent.parent
TEMP_DIR = PROJECT_DIR / "temp"

def get_video_id(url_or_id: str) -> str:
    if len(url_or_id) == 11:
        return url_or_id
    patterns = [
        r'(?:v=|\/v\/|embed\/|youtu\.be\/|\/shorts\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/live\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id

def parse_ytdlp_json(json_str: str, video_id: str, url: str):
    data = json.loads(json_str)
    title = data.get("title", f"YouTube Video {video_id}")
    channel = data.get("uploader", "Unknown")
    upload_date = data.get("upload_date", "")
    
    date_str = "Year 2026"
    if len(upload_date) == 8:
        months = {
            "01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June",
            "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"
        }
        year = upload_date[:4]
        month = months.get(upload_date[4:6], "January")
        date_str = f"{month} {year}"
    
    return {
        "title": title,
        "channel": channel,
        "date": date_str,
        "url": url
    }

def get_video_details(video_id: str):
    url = f"https://www.youtube.com/watch?v={video_id}"
    # Try without cookies first (extremely fast, avoids keychain profile locks)
    try:
        proc = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", url],
            capture_output=True, text=True, timeout=10
        )
        if proc.returncode == 0:
            return parse_ytdlp_json(proc.stdout, video_id, url)
    except Exception as e:
        print(f"Fast metadata extraction failed: {e}")
        
    # Try with cookies as fallback
    try:
        proc = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", "--cookies-from-browser", "chrome", url],
            capture_output=True, text=True, timeout=15
        )
        if proc.returncode == 0:
            return parse_ytdlp_json(proc.stdout, video_id, url)
        else:
            raise RuntimeError(f"yt-dlp with cookies failed: {proc.stderr}")
    except Exception as e:
        print(f"Warning: Could not retrieve all metadata from yt-dlp: {e}")
        return {
            "title": f"YouTube Video {video_id}",
            "channel": "Unknown",
            "date": "Year 2026",
            "url": url
        }

def get_transcript(video_id: str) -> str:
    try:
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id, languages=['en', 'es'])
        text = "\n".join([snippet.text for snippet in fetched.snippets])
        return text
    except Exception as e:
        print(f"youtube-transcript-api failed: {e}. Trying fallback with yt-dlp...", file=sys.stderr)
        
    try:
        import tempfile
        import shutil
        tmp_dir = Path(tempfile.mkdtemp(prefix="yt_curate_"))
        
        subprocess.run(
            [
                "yt-dlp",
                "--write-subs", "--write-auto-subs",
                "--sub-lang", "en,es",
                "--sub-format", "vtt",
                "--skip-download", "--no-warnings",
                "--cookies-from-browser", "chrome",
                "--output", str(tmp_dir / "transcript"),
                f"https://www.youtube.com/watch?v={video_id}"
            ],
            capture_output=True, timeout=60
        )
        
        vtt_files = list(tmp_dir.glob("*.vtt"))
        if not vtt_files:
            raise RuntimeError("No subtitle file (.vtt) was downloaded")
            
        en_vtt = list(tmp_dir.glob("*.en.vtt"))
        vtt_file = en_vtt[0] if en_vtt else vtt_files[0]
        vtt_text = vtt_file.read_text(encoding="utf-8")
        
        lines = vtt_text.splitlines()
        deduped = []
        prev = None
        for line in lines:
            if re.match(r"^(WEBVTT|Kind:|Language:|Style:)", line.strip()):
                continue
            if re.match(r"^\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*", line):
                continue
            if re.match(r"^\d+$", line.strip()):
                continue
            line = re.sub(r"<[^>]+>", "", line).strip()
            if not line:
                continue
            if line != prev:
                deduped.append(line)
            prev = line
            
        shutil.rmtree(tmp_dir, ignore_errors=True)
        return "\n".join(deduped)
    except Exception as e:
        print(f"Critical error obtaining transcript: {e}", file=sys.stderr)
        return ""

def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube metadata and transcript")
    parser.add_argument("--url", required=True, help="YouTube video URL or ID")
    parser.add_argument("--output", help="Optional path to output the JSON data. Defaults to temp/fetched_data.json")
    args = parser.parse_args()
    
    video_id = get_video_id(args.url)
    details = get_video_details(video_id)
    transcript = get_transcript(video_id)
    
    data = {
        "video_id": video_id,
        "metadata": details
    }
    
    output_path = args.output
    if not output_path:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        output_path = TEMP_DIR / "fetched_data.json"
        
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    txt_output_path = Path(output_path).with_suffix(".txt")
    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(transcript)
        
    print(f"Successfully extracted metadata to {output_path} and transcript to {txt_output_path}")

if __name__ == "__main__":
    main()
