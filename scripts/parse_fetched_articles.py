#!/usr/bin/env python3
import sys
from bs4 import BeautifulSoup
from pathlib import Path

def parse_html_file(file_path: Path) -> str:
    content = file_path.read_text(encoding="utf-8", errors="ignore")
    # Split the "Title: Live Content..." header if present
    parts = content.split("---", 1)
    html_content = parts[1] if len(parts) > 1 else content
    
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Extract the main article body
    # Substack usually uses the class "markup" or "body" or similar
    article_body = soup.find(class_="body") or soup.find(class_="markup") or soup.find("article")
    
    if not article_body:
        # Fallback to the whole body if not found
        article_body = soup.find("body") or soup
        
    # We want to preserve basic structure: headings, paragraphs, lists, code
    # We can clean up script, style tags first
    for s in article_body(["script", "style", "noscript", "svg", "button", "picture"]):
        s.decompose()
        
    # Convert elements to simple markdown
    markdown_lines = []
    
    # We can walk through the descendants or children
    for elem in article_body.descendants:
        if elem.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            # Avoid duplicate children content by checking parent
            text = elem.get_text().strip()
            # Clean up anchor buttons inside headers
            if text:
                level = int(elem.name[1])
                markdown_lines.append(f"\n\n{'#' * level} {text}\n")
        elif elem.name == "p":
            text = elem.get_text().strip()
            if text:
                markdown_lines.append(f"\n{text}\n")
        elif elem.name == "li":
            text = elem.get_text().strip()
            if text:
                markdown_lines.append(f"- {text}")
        elif elem.name == "pre" or elem.name == "code":
            # Avoid adding multiple times
            text = elem.get_text().strip()
            if elem.name == "pre" and text:
                markdown_lines.append(f"\n```python\n{text}\n```\n")
            elif elem.name == "code" and not elem.parent.name == "pre" and text:
                markdown_lines.append(f" `{text}` ")
                
    # Since walking descendants adds nested tag contents separately, let's do a cleaner tag-by-tag conversion:
    # Actually, let's write a simple clean-up converter:
    return clean_soup(article_body)

def clean_soup(element) -> str:
    output = []
    
    def walk(node):
        if node.name is None: # text node
            text = node.strip()
            if text:
                output.append(node)
            return
            
        if node.name in ["script", "style", "noscript", "svg", "button", "picture", "header", "footer"]:
            return
            
        if node.name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            level = int(node.name[1])
            # get clean text without nested buttons or anchors
            text = "".join(child.get_text() if child.name not in ["button", "svg"] else "" for child in node.children).strip()
            output.append(f"\n\n{'#' * level} {text}\n")
            return
            
        if node.name == "p":
            # process contents
            text = "".join(child.get_text() if child.name is not None or child.name not in ["button", "svg"] else child for child in node.children).strip()
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
            
    walk(element)
    
    # Join and clean up extra spaces
    text = "".join(output)
    # Deduplicate consecutive newlines
    text = "\n".join(line for line in text.splitlines() if line.strip() or line == "")
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text

if __name__ == "__main__":
    import json
    
    step_files = {
        "article_1": Path("temp/article_1.md"),
        "article_2": Path("temp/article_2.md"),
        "article_3": Path("temp/article_3.md")
    }
    
    temp_dir = Path("temp")
    temp_dir.mkdir(exist_ok=True)
    
    for key, path in step_files.items():
        print(f"Parsing {key}...")
        parsed_text = parse_html_file(path)
        output_path = temp_dir / f"{key}_cleaned.txt"
        output_path.write_text(parsed_text, encoding="utf-8")
        print(f"Saved to {output_path}")
