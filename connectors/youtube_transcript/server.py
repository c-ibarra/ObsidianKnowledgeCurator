"""
yt_transcript_mcp - Local MCP Server to download and clean YouTube transcripts.

Exposes two tools:
  - yt_get_transcript : downloads and cleans the transcript of a YouTube URL
  - yt_list_transcripts: lists transcripts already saved in the local directory

Transport: stdio (for Claude Desktop)
"""

import json
import re
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# =============================================================================
# CONFIGURATION
# =============================================================================

# Base directory where transcripts are saved
TRANSCRIPTS_DIR = Path("/Users/carlosibarra/Downloads/yt-transcripts")

# Preferred languages (in order of priority)
PREFERRED_LANGS = ["es", "en"]

# =============================================================================
# SERVER INITIALIZATION
# =============================================================================

mcp = FastMCP("yt_transcript_mcp")

# =============================================================================
# HELPERS
# =============================================================================

def to_camel_case(text: str) -> str:
    """Converts text to camelCase by removing special characters."""
    # Normalize: lowercase and replace non-ASCII characters
    text = text.lower()
    # Replace common special characters
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n", "ç": "c",
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    # Remove characters that are not letters, numbers, or spaces
    text = re.sub(r"[^a-z0-9 ]", "", text)

    # Convert to camelCase
    words = text.split()
    if not words:
        return "videoTranscript"
    return words[0] + "".join(w.capitalize() for w in words[1:])


def clean_vtt_content(vtt_text: str) -> str:
    """
    Cleans the content of a .vtt file and returns readable plain text.
    Removes: timestamps, headers, HTML tags, consecutive duplicates.
    """
    lines = vtt_text.splitlines()
    clean_lines = []

    for line in lines:
        # Remove WEBVTT header and metadata
        if re.match(r"^(WEBVTT|Kind:|Language:)", line.strip()):
            continue
        # Remove timestamps (00:00:01.000 --> 00:00:03.000)
        if re.match(r"^\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*", line):
            continue
        # Remove line numbers alone
        if re.match(r"^\d+$", line.strip()):
            continue
        # Remove HTML tags (<c>, </c>, <00:00:01.000>, etc.)
        line = re.sub(r"<[^>]+>", "", line)
        # Skip empty lines
        if not line.strip():
            continue
        clean_lines.append(line.strip())

    # Remove consecutive duplicate lines
    deduped = []
    prev = None
    for line in clean_lines:
        if line != prev:
            deduped.append(line)
        prev = line

    return " ".join(deduped)


def find_vtt_file(directory: Path) -> Optional[Path]:
    """
    Searches for the .vtt file in a directory, prioritizing Spanish over English.
    """
    for lang in PREFERRED_LANGS:
        matches = list(directory.glob(f"*.{lang}.vtt"))
        if matches:
            return matches[0]
    # Fallback: any .vtt file
    all_vtt = list(directory.glob("*.vtt"))
    return all_vtt[0] if all_vtt else None


def get_video_title(url: str) -> str:
    """Gets the video title using yt-dlp."""
    result = subprocess.run(
        ["yt-dlp", "--get-title", "--no-warnings", "--cookies-from-browser", "chrome", url],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Could not retrieve title: {result.stderr.strip()}")
    return result.stdout.strip()


def download_vtt(url: str, output_dir: Path) -> None:
    """Downloads the VTT file for the video using yt-dlp."""
    result = subprocess.run(
        [
            "yt-dlp",
            "--write-subs",
            "--write-auto-subs",
            "--sub-lang", ",".join(PREFERRED_LANGS),
            "--sub-format", "vtt",
            "--skip-download",
            "--no-warnings",
            "--cookies-from-browser", "chrome",
            "--retries", "3",
            "--output", str(output_dir / "transcript"),
            url,
        ],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed: {result.stderr.strip()}")

# =============================================================================
# PYDANTIC MODELS
# =============================================================================

class GetTranscriptInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    url: str = Field(
        ...,
        description="URL of the YouTube video (e.g. 'https://www.youtube.com/watch?v=XXXXX')",
        min_length=10,
    )
    title: Optional[str] = Field(
        default=None,
        description="Title of the video (optional). If not provided, it is retrieved automatically.",
        max_length=200,
    )
    save_file: bool = Field(
        default=True,
        description="If True, saves the transcript as a .txt file in ~/Downloads/yt-transcripts/<camelCase>/",
    )


class ListTranscriptsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(
        default=20,
        description="Maximum number of transcripts to list",
        ge=1,
        le=100,
    )

# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool(
    name="yt_get_transcript",
    annotations={
        "title": "Download and clean YouTube transcript",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def yt_get_transcript(params: GetTranscriptInput) -> str:
    """
    Downloads the transcript (subtitles) of a YouTube video, cleans it
    and optionally saves it as a .txt file.

    Process:
    1. Obtains the video title (or uses the provided one)
    2. Downloads the .vtt with yt-dlp (prioritizing Spanish over English if preferred)
    3. Cleans timestamps, HTML tags, and duplicates
    4. Saves to ~/Downloads/yt-transcripts/<camelCase>/<camelCase>.txt

    Args:
        params (GetTranscriptInput):
            - url (str): YouTube video URL
            - title (Optional[str]): Manual title (avoids extra yt-dlp call)
            - save_file (bool): Whether to save the .txt locally (default: True)

    Returns:
        str: JSON with fields:
            - success (bool)
            - title (str): Title of the video
            - folder_name (str): camelCase name used for the folder
            - output_path (str): Saved file path (if save_file=True)
            - transcript (str): Clean transcript text
            - word_count (int): Word count
            - error (str): Error message if success=False
    """
    tmp_dir = None
    try:
        # --- Step 1: Get Title ---
        if params.title:
            video_title = params.title
        else:
            video_title = get_video_title(params.url)

        folder_name = to_camel_case(video_title) or "videoTranscript"

        # --- Step 2: Download .vtt to temp directory ---
        tmp_dir = Path(tempfile.mkdtemp(prefix="yt_mcp_"))
        download_vtt(params.url, tmp_dir)

        # --- Step 3: Find and read the .vtt file ---
        vtt_file = find_vtt_file(tmp_dir)
        if not vtt_file:
            return json.dumps({
                "success": False,
                "error": "VTT file not found. The video may not have subtitles available.",
            })

        vtt_text = vtt_file.read_text(encoding="utf-8")

        # --- Step 4: Clean the transcript ---
        clean_text = clean_vtt_content(vtt_text)
        if not clean_text.strip():
            return json.dumps({
                "success": False,
                "error": "The transcript is empty after cleaning.",
            })

        # --- Step 5: Save as .txt (optional) ---
        output_path = ""
        if params.save_file:
            dest_dir = TRANSCRIPTS_DIR / folder_name
            dest_dir.mkdir(parents=True, exist_ok=True)
            output_file = dest_dir / f"{folder_name}.txt"
            output_file.write_text(clean_text, encoding="utf-8")
            output_path = str(output_file)

        word_count = len(clean_text.split())

        return json.dumps({
            "success": True,
            "title": video_title,
            "folder_name": folder_name,
            "output_path": output_path,
            "transcript": clean_text,
            "word_count": word_count,
        }, ensure_ascii=False)

    except subprocess.TimeoutExpired:
        return json.dumps({"success": False, "error": "Timeout executing yt-dlp. Check your connection."})
    except RuntimeError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Unexpected error: {type(e).__name__}: {e}"})
    finally:
        # Always clean up temp directory
        if tmp_dir and tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)


@mcp.tool(
    name="yt_list_transcripts",
    annotations={
        "title": "List saved transcripts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def yt_list_transcripts(params: ListTranscriptsInput) -> str:
    """
    Lists transcripts already saved in ~/Downloads/yt-transcripts/.

    Args:
        params (ListTranscriptsInput):
            - limit (int): Maximum results to return (default: 20)

    Returns:
        str: JSON with fields:
            - success (bool)
            - base_dir (str): Transcripts base directory
            - total (int): Total transcripts found
            - transcripts (list): List with name, path, size_kb, word_count
    """
    try:
        if not TRANSCRIPTS_DIR.exists():
            return json.dumps({
                "success": True,
                "base_dir": str(TRANSCRIPTS_DIR),
                "total": 0,
                "transcripts": [],
            })

        transcripts = []
        folders = sorted(TRANSCRIPTS_DIR.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)

        for folder in folders[:params.limit]:
            if not folder.is_dir():
                continue
            txt_files = list(folder.glob("*.txt"))
            if not txt_files:
                continue
            txt_file = txt_files[0]
            content = txt_file.read_text(encoding="utf-8")
            transcripts.append({
                "name": folder.name,
                "path": str(txt_file),
                "size_kb": round(txt_file.stat().st_size / 1024, 2),
                "word_count": len(content.split()),
            })

        return json.dumps({
            "success": True,
            "base_dir": str(TRANSCRIPTS_DIR),
            "total": len(transcripts),
            "transcripts": transcripts,
        }, ensure_ascii=False)

    except Exception as e:
        return json.dumps({"success": False, "error": f"Error: {type(e).__name__}: {e}"})


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # stdio transport — Claude Desktop manages the process
    mcp.run()
