#!/usr/bin/env python3
import os
import sys
import re
import time
import json
import argparse
import subprocess
import urllib.request
import urllib.parse
from pathlib import Path
from bs4 import BeautifulSoup
import requests

PROJECT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_DIR))

from src.config import PROJECT_ROOT, VAULT_ROOT, ASSETS_IMAGES_DIR, TEMP_DIR
from scripts.graphify_mapper import map_context_with_graphify

TEMP_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# AUDIO / PODCAST AUTO-DETECTION
# ==============================================================================

def is_audio_or_podcast_url(url: str) -> bool:
    """Check if the URL points to a podcast portal, RSS feed, or media file."""
    url_lower = url.lower()
    audio_patterns = [
        r"\.mp3(\?.*)?$", r"\.m4a(\?.*)?$", r"\.wav(\?.*)?$", r"\.ogg(\?.*)?$",
        r"siemens\.fm", r"spotify\.com/episode", r"podcasts\.apple\.com",
        r"anchor\.fm", r"buzzsprout\.com", r"libsyn\.com"
    ]
    return any(re.search(pat, url_lower) for pat in audio_patterns)

def delegate_to_podcast_fetcher(url: str) -> dict:
    """Delegate processing to fetch_podcast_data.py."""
    print(f"[Article Extractor] Audio/Podcast URL detected! Delegating to fetch_podcast_data.py...", file=sys.stderr)
    from scripts.fetch_podcast_data import extract_podcast_episode
    return extract_podcast_episode(url)

# ==============================================================================
# MCP FETCH INTEGRATION (TIER 1 SCRAPING ENGINE)
# ==============================================================================

def fetch_via_mcp(url: str) -> str:
    """
    Attempts to fetch webpage content using the official mcp-server-fetch.
    """
    print(f"Attempting to fetch via mcp-server-fetch for URL: {url}...", file=sys.stderr)
    try:
        proc = subprocess.Popen(
            ["uv", "run", "scripts/run_fetch.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "okc-fetch-client", "version": "1.0"}
            }
        }
        proc.stdin.write(json.dumps(init_req) + "\n")
        proc.stdin.flush()
        
        init_res_line = ""
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            try:
                data = json.loads(line)
                if data.get("id") == 1:
                    init_res_line = line
                    break
            except json.JSONDecodeError:
                continue
                
        if not init_res_line:
            return ""
            
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        proc.stdin.write(json.dumps(initialized_notification) + "\n")
        proc.stdin.flush()
        
        call_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "fetch",
                "arguments": {"url": url}
            }
        }
        proc.stdin.write(json.dumps(call_req) + "\n")
        proc.stdin.flush()
        
        call_res_line = ""
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            try:
                data = json.loads(line)
                if data.get("id") == 2:
                    call_res_line = line
                    break
            except json.JSONDecodeError:
                continue
                
        proc.terminate()
        proc.wait()
        
        if not call_res_line:
            return ""
            
        res = json.loads(call_res_line)
        content_list = res.get("result", {}).get("content", [])
        if content_list:
            text = content_list[0].get("text", "")
            return text
            
    except Exception as e:
        print(f"Exception during Fetch MCP communication: {e}", file=sys.stderr)
        
    return ""

def is_blocked_or_restricted(text: str) -> bool:
    """Check if the extracted text contains blocking indicators (robots.txt, captchas, login walls)."""
    if len(text.strip()) < 400:
        return True
    blocked_keywords = [
        "robots.txt", "sign in to continue", "login required",
        "access to linkedin without the express permission",
        "please enable javascript", "captcha", "cloudflare"
    ]
    text_lower = text.lower()
    return any(kw in text_lower for kw in blocked_keywords)

def fetch_tier1_trafilatura(url: str) -> tuple[str, str]:
    """Tier 1: Try MCP fetch or trafilatura/requests."""
    mcp_content = fetch_via_mcp(url)
    if mcp_content and not is_blocked_or_restricted(mcp_content):
        # Extract title and body
        lines = mcp_content.splitlines()
        title = lines[0].replace("#", "").strip() if lines else "Web Article"
        return title, mcp_content
    return "", ""

def fetch_tier2_readability(url: str) -> tuple[str, str]:
    """Tier 2: Try direct requests with browser user-agent and BeautifulSoup DOM parsing."""
    print(f"[Tier 2 Fallback] Fetching DOM directly with browser User-Agent for {url}...", file=sys.stderr)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    try:
        import ssl
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
            
        soup = BeautifulSoup(html, "html.parser")
        title_el = soup.find("title") or soup.find("h1")
        title = title_el.get_text().strip() if title_el else "Web Article"
        
        # Remove unwanted tags
        for el in soup(["script", "style", "nav", "footer", "header", "form"]):
            el.decompose()
            
        # Get paragraph text
        paragraphs = [p.get_text().strip() for p in soup.find_all(["p", "h2", "h3"]) if len(p.get_text().strip()) > 30]
        body = "\n\n".join(paragraphs)
        if len(body) > 300 and not is_blocked_or_restricted(body):
            return title, body
    except Exception as err:
        print(f"[Tier 2 Error] {err}", file=sys.stderr)
        
    return "", ""

# ==============================================================================
# IMAGE EXTRACTION & LOCAL DOWNLOAD HELPER
# ==============================================================================

def download_article_images(url: str, text: str, title: str) -> tuple[str, list[dict]]:
    """
    Finds all image links in text (markdown or html), downloads them to VAULT_ROOT/assets/images/,
    and replaces remote links with local Obsidian asset links.
    """
    slug = re.sub(r"[^\w\s-]", "", title.lower())
    slug = re.sub(r"[-\s]+", "-", slug).strip("-")[:40] or "article"

    assets_dir = ASSETS_IMAGES_DIR
    assets_dir.mkdir(parents=True, exist_ok=True)

    md_img_pattern = r"!\[([^\]]*)\]\((https?://[^\)]+)\)"
    matches = re.findall(md_img_pattern, text)
    
    downloaded_records = []
    updated_text = text

    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for idx, (alt, img_url) in enumerate(matches, 1):
        try:
            ext = "png"
            if ".jpg" in img_url.lower() or ".jpeg" in img_url.lower():
                ext = "jpg"
            elif ".webp" in img_url.lower():
                ext = "webp"
            elif ".gif" in img_url.lower():
                ext = "gif"
            elif ".svg" in img_url.lower():
                ext = "svg"
                
            file_name = f"{slug}-img-{idx:02d}.{ext}"
            file_path = assets_dir / file_name

            headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            req = urllib.request.Request(img_url, headers=headers)
            with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
                img_bytes = resp.read()
                if len(img_bytes) > 500:
                    with open(file_path, "wb") as f:
                        f.write(img_bytes)
                    
                    # Sanitize downloaded image (strip C2PA / EXIF / AI metadata)
                    try:
                        from src.agent_tools.sanitizer import sanitize_image
                        sanitize_image(file_path)
                    except Exception as san_err:
                        print(f"[Sanitizer Warning] Could not sanitize image {file_name}: {san_err}", file=sys.stderr)

                    old_link = f"![{alt}]({img_url})"
                    new_link = f"![{alt}](assets/images/{file_name})\n![[{file_name}]]"
                    updated_text = updated_text.replace(old_link, new_link)
                    downloaded_records.append({
                        "original_url": img_url,
                        "local_file": file_name,
                        "local_path": str(file_path)
                    })
                    print(f"[Image Downloader] Saved and sanitized image {idx}: {file_name}", file=sys.stderr)
        except Exception as err:
            print(f"[Image Downloader Warning] Failed to download {img_url}: {err}", file=sys.stderr)

    return updated_text, downloaded_records

# ==============================================================================
# MAIN ROUTINE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Fetch article web page data with 3-tier fallback & Graphify context")
    parser.add_argument("--url", required=True, help="Webpage URL to scrape")
    parser.add_argument("--output", help="Optional output JSON file path. Defaults to temp/fetched_data.json")
    args = parser.parse_args()
    
    url = args.url

    # Check for Audio / Podcast redirection
    if is_audio_or_podcast_url(url):
        delegate_to_podcast_fetcher(url)
        sys.exit(0)

    title, markdown_body = "", ""

    # Tier 1 Attempt
    title, markdown_body = fetch_tier1_trafilatura(url)
    
    # Tier 2 Attempt if Tier 1 failed or was restricted
    if not markdown_body or is_blocked_or_restricted(markdown_body):
        print("[Article Extractor] Tier 1 failed or restricted. Escalating to Tier 2...", file=sys.stderr)
        title, markdown_body = fetch_tier2_readability(url)

    # Fallback default values if all tiers failed
    if not title:
        try:
            domain = urllib.parse.urlparse(url).netloc
            title = f"Web Article from {domain}"
        except Exception:
            title = "Web Article"

    if not markdown_body:
        markdown_body = f"Title: {title}\nSource: {url}\n\n[Content blocked or requires interactive session. Use read_url_content or manual summary.]"

    # Download source images locally
    markdown_body, downloaded_images = download_article_images(url, markdown_body, title)

    # Universal Hygiene & Sanitization
    try:
        from src.agent_tools.sanitizer import sanitize_text
        title = sanitize_text(title)
        markdown_body = sanitize_text(markdown_body)
    except Exception as san_err:
        print(f"[Sanitizer Warning] Could not sanitize article text: {san_err}", file=sys.stderr)

    # Graphify Context Enriched Mapping
    graphify_ctx = map_context_with_graphify(title, markdown_body[:2000])

    current_time = time.localtime()
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    date_str = f"{months[current_time.tm_mon - 1]} {current_time.tm_year}"
    
    data = {
        "url": url,
        "metadata": {
            "title": title,
            "channel": "Web Article",
            "date": date_str,
            "url": url,
            "images_downloaded": len(downloaded_images),
            "downloaded_images": downloaded_images
        },
        "graphify_context": graphify_ctx
    }
    
    output_path = args.output
    if not output_path:
        TEMP_DIR.mkdir(parents=True, exist_ok=True)
        output_path = TEMP_DIR / "fetched_data.json"
        
    output_path = Path(output_path)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        
    txt_output_path = output_path.with_suffix(".txt")
    with open(txt_output_path, "w", encoding="utf-8") as f:
        f.write(markdown_body)
        
    print(f"Successfully scraped metadata to {output_path} and parsed body to {txt_output_path}")

if __name__ == "__main__":
    main()
