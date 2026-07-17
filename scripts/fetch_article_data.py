#!/usr/bin/env python3
import os
import sys
import re
import time
import json
import argparse
import subprocess
import urllib.request
from pathlib import Path
from bs4 import BeautifulSoup
import requests

PROJECT_DIR = Path(__file__).parent.parent
TEMP_DIR = PROJECT_DIR / "temp"

def check_chrome():
    paths = [
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
        "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
        "/usr/bin/google-chrome"
    ]
    for p in paths:
        if os.path.exists(p):
            return p
    return None

def fetch_dynamic_dom(url: str, delay: int = 8) -> str:
    chrome_path = check_chrome()
    if not chrome_path:
        print("Google Chrome executable not found on this system.", file=sys.stderr)
        return ""
        
    print(f"Launching Chrome Canary/Chrome in background: {chrome_path}", file=sys.stderr)
    
    # Start Chrome with remote debugging enabled
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--remote-debugging-port=9222",
        "--remote-allow-origins=*",
        "--no-sandbox",
        url
    ]
    
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    print(f"Waiting {delay} seconds for client-side JavaScript to render page...", file=sys.stderr)
    time.sleep(delay)
    
    dom_content = ""
    try:
        # Get target page targets from CDP
        req = urllib.request.urlopen("http://localhost:9222/json", timeout=5)
        targets = json.loads(req.read().decode('utf-8'))
        
        ws_url = None
        for t in targets:
            if t.get('type') == 'page':
                ws_url = t.get('webSocketDebuggerUrl')
                break
                
        if not ws_url:
            raise RuntimeError("Could not find any active page target WebSocket debugging URL.")
            
        print(f"Connecting to page WebSocket: {ws_url}", file=sys.stderr)
        
        import websocket
        ws = websocket.create_connection(ws_url, timeout=10)
        
        # Execute JS evaluation on the page DOM
        eval_cmd = {
            "id": 1,
            "method": "Runtime.evaluate",
            "params": {
                "expression": "document.documentElement.outerHTML",
                "returnByValue": True
            }
        }
        ws.send(json.dumps(eval_cmd))
        
        response = ws.recv()
        result = json.loads(response)
        dom_content = result.get('result', {}).get('result', {}).get('value', '')
        ws.close()
        
        if dom_content:
            print("Successfully extracted fully rendered DOM via CDP.", file=sys.stderr)
        else:
            print(f"Empty DOM returned. Result: {result}", file=sys.stderr)
            
    except Exception as e:
        print(f"Error during Chrome DevTools Protocol execution: {e}", file=sys.stderr)
    finally:
        print("Terminating background Chrome process...", file=sys.stderr)
        process.terminate()
        process.wait()
        
    return dom_content

def fetch_static_html(url: str) -> str:
    print(f"Fetching static HTML from URL: {url}", file=sys.stderr)
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        return res.text
    except Exception as e:
        print(f"Error fetching static HTML: {e}", file=sys.stderr)
        return ""

def clean_html_to_markdown(html_content: str) -> tuple[str, str]:
    """
    Parses HTML content, extracts the title and formats the body into clean markdown.
    Returns (title, markdown_body).
    """
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    
    # Try finding page header if title is generic
    if not title or title.lower() in ["live content", "untitled", "home", "index"]:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text().strip()
    if not title:
        title = "Web Article"
        
    # Standardize spaces in title
    title = re.sub(r'\s+', ' ', title)
    
    # Identify the main article body content
    # We prioritize common article wrapper classes
    article_body = (
        soup.find(class_="body") or 
        soup.find(class_="markup") or 
        soup.find("article") or
        soup.find(id="main-content") or
        soup.find("main") or
        soup.find("body") or
        soup
    )
    
    # Strip unnecessary element types
    for s in article_body(["script", "style", "noscript", "svg", "button", "picture", "header", "footer", "nav"]):
        s.decompose()
        
    # Convert tag hierarchy to markdown
    output = []
    
    def walk(node):
        if node.name is None:  # Text node
            text = node.strip()
            if text:
                output.append(node)
            return
            
        if node.name in ["script", "style", "noscript", "svg", "button", "picture", "header", "footer", "nav"]:
            return
            
        if node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(node.name[1])
            # get clean text without nested buttons or anchors
            text = "".join(child.get_text() if child.name not in ["button", "svg"] else "" for child in node.children).strip()
            output.append(f"\n\n{'#' * level} {text}\n")
            return
            
        if node.name == "p":
            text = "".join(child.get_text() if child.name is None or child.name not in ["button", "svg"] else child for child in node.children).strip()
            if text:
                output.append(f"\n{text}\n")
            return
            
        if node.name == "pre":
            text = node.get_text().strip()
            output.append(f"\n```python\n{text}\n```\n")
            return
            
        if node.name == "code" and (node.parent is None or node.parent.name != "pre"):
            text = node.get_text().strip()
            output.append(f" `{text}` ")
            return
            
        if node.name == "li":
            text = node.get_text().strip()
            output.append(f"\n- {text}")
            return
            
        if node.name == "ul" or node.name == "ol":
            for child in node.children:
                walk(child)
            output.append("\n")
            return
            
        for child in node.children:
            walk(child)
            
    walk(article_body)
    
    # Format and deduplicate lines
    text_content = "".join(output)
    lines = [line.strip() for line in text_content.splitlines()]
    
    # Deduplicate consecutive empty lines
    cleaned_lines = []
    prev_empty = False
    for line in lines:
        if line == "":
            if not prev_empty:
                cleaned_lines.append("")
                prev_empty = True
        else:
            cleaned_lines.append(line)
            prev_empty = False
            
    markdown_body = "\n".join(cleaned_lines).strip()
    markdown_body = re.sub(r'\n{3,}', '\n\n', markdown_body)
    
    return title, markdown_body

def main():
    parser = argparse.ArgumentParser(description="Fetch article web page data (supports static and dynamic dynamic rendering)")
    parser.add_argument("--url", required=True, help="Webpage URL to scrape")
    parser.add_argument("--dynamic", action="store_true", help="Force dynamic client-side JS rendering using headless Chrome and CDP")
    parser.add_argument("--delay", type=int, default=8, help="JavaScript execution buffer loading delay in seconds (default: 8)")
    parser.add_argument("--output", help="Optional output JSON file path. Defaults to temp/fetched_data.json")
    args = parser.parse_args()
    
    url = args.url
    
    # Auto-detect dynamic platform patterns (like gemini share links)
    is_dynamic = args.dynamic or "share.gemini.google" in url or "gemini.google.com" in url
    
    if is_dynamic:
        html = fetch_dynamic_dom(url, delay=args.delay)
    else:
        html = fetch_static_html(url)
        # If static fetch yields nothing or minimal headers, fall back to dynamic automatically
        if not html or len(html) < 2000:
            print("Static fetch empty or restricted. Trying fallback dynamic Chrome fetch...", file=sys.stderr)
            html = fetch_dynamic_dom(url, delay=args.delay)
            
    if not html:
        print("Error: Could not retrieve webpage HTML content.", file=sys.stderr)
        sys.exit(1)
        
    title, markdown_body = clean_html_to_markdown(html)
    
    # Format date for metadata
    current_time = time.localtime()
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    date_str = f"{months[current_time.tm_mon - 1]} {current_time.tm_year}"
    
    # Setup metadata matching fetch_youtube_data structure
    data = {
        "url": url,
        "metadata": {
            "title": title,
            "channel": "Web Article",
            "date": date_str,
            "url": url
        }
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
