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
TEMP_DIR = PROJECT_DIR / "temp"

# ==============================================================================
# MCP FETCH INTEGRATION (PRIMARY SCRAIPING ENGINE)
# ==============================================================================

def fetch_via_mcp(url: str) -> str:
    """
    Attempts to fetch webpage content using the official mcp-server-fetch.
    Spawns 'uvx mcp-server-fetch' as an on-demand stdio subprocess and communicates via JSON-RPC.
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
        
        # 1. Send initialize request
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
        
        # Read initialize response (loop until id == 1 is found)
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
            print("Failed to initialize Fetch MCP server.", file=sys.stderr)
            return ""
            
        # 2. Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        proc.stdin.write(json.dumps(initialized_notification) + "\n")
        proc.stdin.flush()
        
        # 3. Call fetch tool
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
        
        # Read tools/call response (loop until id == 2 is found)
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
                
        # Terminate process cleanly
        proc.terminate()
        proc.wait()
        
        if not call_res_line:
            print("No response from Fetch MCP server.", file=sys.stderr)
            return ""
            
        res = json.loads(call_res_line)
        if "error" in res:
            print(f"MCP Tool returned error: {res['error']}", file=sys.stderr)
            return ""
            
        content_list = res.get("result", {}).get("content", [])
        if content_list:
            text = content_list[0].get("text", "")
            return text
            
    except Exception as e:
        print(f"Exception during Fetch MCP communication: {e}", file=sys.stderr)
        
    return ""

def parse_mcp_markdown(mcp_text: str, url: str) -> tuple[str, str]:
    """
    Parses title and cleans body content from raw MCP markdown output.
    """
    lines = mcp_text.splitlines()
    title = ""
    
    # Try finding the first markdown heading for title
    for line in lines:
        match = re.match(r"^#+\s+(.*)$", line)
        if match:
            title = match.group(1).strip()
            break
            
    if not title:
        # Fallback to domain name from URL
        try:
            domain = urllib.parse.urlparse(url).netloc
            title = f"Web Article from {domain}"
        except Exception:
            title = "Web Article"
            
    # Clean up introductory "Contents of URL" line if present
    body_lines = lines
    if body_lines and body_lines[0].startswith("Contents of "):
        body_lines = body_lines[1:]
        
    markdown_body = "\n".join(body_lines).strip()
    return title, markdown_body

# ==============================================================================
# LEGACY SCRAPING FALLBACKS
# ==============================================================================

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
    soup = BeautifulSoup(html_content, "html.parser")
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()
    
    if not title or title.lower() in ["live content", "untitled", "home", "index"]:
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text().strip()
    if not title:
        title = "Web Article"
        
    title = re.sub(r'\s+', ' ', title)
    
    article_body = (
        soup.find(class_="body") or 
        soup.find(class_="markup") or 
        soup.find("article") or
        soup.find(id="main-content") or
        soup.find("main") or
        soup.find("body") or
        soup
    )
    
    for s in article_body(["script", "style", "noscript", "svg", "button", "picture", "header", "footer", "nav"]):
        s.decompose()
        
    output = []
    
    def walk(node):
        if node.name is None:
            text = node.strip()
            if text:
                output.append(node)
            return
            
        if node.name in ["script", "style", "noscript", "svg", "button", "picture", "header", "footer", "nav"]:
            return
            
        if node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(node.name[1])
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
    
    text_content = "".join(output)
    lines = [line.strip() for line in text_content.splitlines()]
    
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

# ==============================================================================
# MAIN ROUTINE
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Fetch article web page data (supports Fetch MCP and legacy scrapers)")
    parser.add_argument("--url", required=True, help="Webpage URL to scrape")
    parser.add_argument("--dynamic", action="store_true", help="Force dynamic legacy Chrome CDP rendering")
    parser.add_argument("--delay", type=int, default=8, help="JS rendering buffer delay in seconds (default: 8)")
    parser.add_argument("--output", help="Optional output JSON file path. Defaults to temp/fetched_data.json")
    args = parser.parse_args()
    
    url = args.url
    mcp_success = False
    title = ""
    markdown_body = ""
    
    # 1. Attempt Primary Scraping Engine (Fetch MCP) unless dynamic is forced
    if not args.dynamic:
        mcp_content = fetch_via_mcp(url)
        if mcp_content:
            print("Successfully extracted webpage content via Fetch MCP.", file=sys.stderr)
            title, markdown_body = parse_mcp_markdown(mcp_content, url)
            mcp_success = True
            
    # 2. Fall back to Legacy Scraper (Static or Dynamic Chrome CDP)
    if not mcp_success:
        print("Falling back to legacy scraping engines...", file=sys.stderr)
        is_dynamic = args.dynamic or "share.gemini.google" in url or "gemini.google.com" in url
        
        html = ""
        if is_dynamic:
            html = fetch_dynamic_dom(url, delay=args.delay)
        else:
            html = fetch_static_html(url)
            if not html or len(html) < 2000:
                print("Static fetch empty or restricted. Trying fallback dynamic Chrome fetch...", file=sys.stderr)
                html = fetch_dynamic_dom(url, delay=args.delay)
                
        if not html:
            print("Error: Could not retrieve webpage HTML content via legacy scrapers.", file=sys.stderr)
            sys.exit(1)
            
        title, markdown_body = clean_html_to_markdown(html)
        
    # Format metadata matching fetch_youtube_data structure
    current_time = time.localtime()
    months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
    date_str = f"{months[current_time.tm_mon - 1]} {current_time.tm_year}"
    
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
