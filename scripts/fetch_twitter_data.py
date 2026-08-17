#!/usr/bin/env python3
import os
import sys
import re
import argparse
import subprocess
import json
import tempfile
import shutil
from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import PROJECT_ROOT, VAULT_ROOT, TEMP_DIR

TEMP_DIR.mkdir(parents=True, exist_ok=True)

def parse_twitter_ytdlp_json(json_str: str, url: str):
    data = json.loads(json_str)
    title = data.get("title", "Twitter Video / Post")
    uploader = data.get("uploader", data.get("uploader_id", "Unknown"))
    uploader_id = data.get("uploader_id", uploader)
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
        "channel": f"@{uploader_id}" if not uploader_id.startswith("@") else uploader_id,
        "date": date_str,
        "url": url
    }

def get_twitter_metadata(url: str):
    # Try without cookies first
    try:
        proc = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", url],
            capture_output=True, text=True, timeout=15
        )
        if proc.returncode == 0:
            return parse_twitter_ytdlp_json(proc.stdout, url)
    except Exception as e:
        print(f"Fast Twitter metadata extraction failed: {e}", file=sys.stderr)
        
    # Try with cookies as fallback
    try:
        proc = subprocess.run(
            ["yt-dlp", "--dump-json", "--no-warnings", "--cookies-from-browser", "chrome", url],
            capture_output=True, text=True, timeout=20
        )
        if proc.returncode == 0:
            return parse_twitter_ytdlp_json(proc.stdout, url)
    except Exception as e:
        print(f"Metadata fallback failed: {e}", file=sys.stderr)
        
    return {
        "title": "X (Twitter) Post / Video",
        "channel": "Twitter User",
        "date": "Year 2026",
        "url": url
    }

def get_twitter_transcript(url: str) -> str:
    # Step 1: Try downloading subtitles via yt-dlp
    tmp_dir = Path(tempfile.mkdtemp(prefix="tw_curate_"))
    try:
        subprocess.run(
            [
                "yt-dlp",
                "--write-subs", "--write-auto-subs",
                "--sub-lang", "en,es",
                "--sub-format", "vtt",
                "--skip-download", "--no-warnings",
                "--output", str(tmp_dir / "transcript"),
                url
            ],
            capture_output=True, timeout=30
        )
        
        vtt_files = list(tmp_dir.glob("*.vtt"))
        if vtt_files:
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
                if not line or line == prev:
                    continue
                deduped.append(line)
                prev = line
                
            shutil.rmtree(tmp_dir, ignore_errors=True)
            return "\n".join(deduped)
    except Exception as e:
        print(f"Subtitle download for X video failed: {e}", file=sys.stderr)
    finally:
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)

    # Step 2: Fallback - Download audio & transcribe using Buzz CLI (Whisper)
    print("No subtitles available for X video. Downloading audio and running Buzz CLI (Whisper)...", file=sys.stderr)
    try:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        tweet_id_match = re.search(r'status/(\d+)', url)
        tweet_id = tweet_id_match.group(1) if tweet_id_match else "twitter_video"
        audio_dest = TEMP_DIR / f"{tweet_id}_audio"
        
        # Download audio via yt-dlp
        subprocess.run(
            [
                "yt-dlp",
                "-x", "--audio-format", "mp3",
                "--no-warnings",
                "-o", f"{audio_dest}.%(ext)s",
                url
            ],
            capture_output=True, check=True, timeout=120
        )
        
        mp3_path = Path(f"{audio_dest}.mp3")
        if not mp3_path.exists():
            raise RuntimeError("MP3 audio file was not created by yt-dlp")
            
        print("Running Buzz CLI transcription (base model)...", file=sys.stderr)
        buzz_bin = "/Applications/Buzz.app/Contents/MacOS/Buzz"
        if Path(buzz_bin).exists():
            subprocess.run(
                [
                    buzz_bin,
                    "add", "--txt", "--hide-gui",
                    "-s", "base", "-l", "en",
                    "-d", str(TEMP_DIR),
                    str(mp3_path)
                ],
                capture_output=True, check=True, timeout=300
            )
            
            txt_files = list(TEMP_DIR.glob(f"{tweet_id}_audio*.txt"))
            if txt_files:
                transcription_txt = txt_files[0]
                text_content = transcription_txt.read_text(encoding="utf-8")
                
                try:
                    mp3_path.unlink()
                    transcription_txt.unlink()
                except Exception as cleanup_err:
                    print(f"Warning during temp cleanup: {cleanup_err}", file=sys.stderr)
                    
                return text_content
        else:
            print("Buzz CLI is not installed at /Applications/Buzz.app. Checking for whisper CLI...", file=sys.stderr)
            # Try whisper CLI if available
            subprocess.run(
                ["whisper", str(mp3_path), "--model", "base", "--output_dir", str(TEMP_DIR), "--output_format", "txt"],
                capture_output=True, check=True, timeout=300
            )
            txt_path = TEMP_DIR / f"{mp3_path.stem}.txt"
            if txt_path.exists():
                text_content = txt_path.read_text(encoding="utf-8")
                mp3_path.unlink()
                txt_path.unlink()
                return text_content

    except Exception as err:
        print(f"Audio transcription for X video failed: {err}", file=sys.stderr)

    return ""

def main():
    parser = argparse.ArgumentParser(description="Fetch Twitter/X metadata and transcribe video audio")
    parser.add_argument("--url", required=True, help="Twitter/X post URL")
    parser.add_argument("--output", help="Optional path to output the JSON data. Defaults to temp/fetched_data.json")
    args = parser.parse_args()
    
    metadata = get_twitter_metadata(args.url)
    transcript = get_twitter_transcript(args.url)

    # Universal Hygiene & Sanitization
    try:
        from src.agent_tools.sanitizer import sanitize_text
        transcript = sanitize_text(transcript)
        if "title" in metadata:
            metadata["title"] = sanitize_text(metadata["title"])
        if "description" in metadata:
            metadata["description"] = sanitize_text(metadata["description"])
    except Exception as san_err:
        print(f"[Sanitizer Warning] Could not sanitize twitter data: {san_err}", file=sys.stderr)

    try:
        from scripts.graphify_mapper import map_context_with_graphify
        graphify_ctx = map_context_with_graphify(metadata.get("title", "Twitter Post"), transcript[:2000])
    except Exception as err:
        graphify_ctx = {"suggested_category": "AI Safety & Governance", "error": str(err)}

    data = {
        "url": args.url,
        "metadata": metadata,
        "graphify_context": graphify_ctx
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
