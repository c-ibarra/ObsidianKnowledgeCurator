#!/usr/bin/env python3
import os
import re
import argparse
from pathlib import Path

def clean_srt(srt_content: str) -> str:
    """
    Cleans WebVTT (.vtt) and SubRip (.srt) subtitle files by removing headers,
    timestamps, and frame indices, then joining lines into paragraphs.
    """
    # Remove WEBVTT header and common metadata lines
    content = re.sub(r'^(WEBVTT|Kind:|Language:|Style:).*?\n', '', srt_content, flags=re.MULTILINE)
    
    # Remove subtitle timestamps (e.g., 00:00:10.000 --> 00:00:15.000)
    content = re.sub(r'(?:\d{2,}:)?\d{2}:\d{2}[\.,]\d{3}\s*-->\s*(?:\d{2,}:)?\d{2}:\d{2}[\.,]\d{3}.*?\n', '', content)
    
    # Remove standalone subtitle indices (numbers on a line by themselves)
    content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
    
    # Clean up empty lines
    lines = [line.strip() for line in content.splitlines() if line.strip()]
    
    # Merge lines to form paragraphs, keeping track of sentences
    merged_text = []
    current_sentence = []
    
    for line in lines:
        current_sentence.append(line)
        if line.endswith(('.', '?', '!')):
            merged_text.append(" ".join(current_sentence))
            current_sentence = []
            
    if current_sentence:
        merged_text.append(" ".join(current_sentence))
        
    return "\n\n".join(merged_text)

def clean_html(html_content: str) -> str:
    """
    Extracts plain text from HTML content by stripping HTML tags and excess spaces.
    """
    content = re.sub(r'<[^>]+>', '', html_content)
    content = re.sub(r'\s+', ' ', content).strip()
    return content

def extract_course(source_dir: Path, output_dir: Path):
    if not source_dir.exists():
        print(f"Error: Source directory '{source_dir}' does not exist.")
        return
        
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Extracting course from: {source_dir}")
    print(f"Output directory: {output_dir}")
    
    # List all subfolders in source_dir
    subfolders = [d for d in source_dir.iterdir() if d.is_dir()]
    
    # Sort subfolders by numerical prefix (e.g., "01. Introduction", "02_Setup")
    def get_prefix(p: Path):
        match = re.match(r'^(\d+)', p.name)
        return int(match.group(1)) if match else 999
    
    subfolders.sort(key=get_prefix)
    
    if not subfolders:
        # If no subfolders, treat the source directory itself as a single section folder
        print("No subfolders found. Processing source directory files directly...")
        subfolders = [source_dir]
    
    for subfolder in subfolders:
        # Avoid processing output or temp directories if they happen to be inside
        if subfolder.resolve() == output_dir.resolve():
            continue
            
        print(f"Processing folder: {subfolder.name}")
        
        # If processing source_dir directly, use a general output name
        filename_base = subfolder.name if subfolder != source_dir else "course_content"
        output_file = output_dir / f"{filename_base}.txt"
        
        # Get all files in this folder
        files = list(subfolder.glob("*"))
        
        # Sort files by their starting number to preserve logical course order (e.g., "1.1 Video.srt")
        def get_file_num(f: Path):
            match = re.match(r'^(\d+[\.\d]*)', f.name)
            if match:
                try:
                    return float(match.group(1).rstrip('.'))
                except ValueError:
                    pass
            return 999.0
            
        files.sort(key=get_file_num)
        
        extracted_sections = []
        
        for file in files:
            if file.suffix in [".srt", ".vtt"]:
                title = file.name.replace(".en_US.srt", "").replace(".en_US.vtt", "").replace(".srt", "").replace(".vtt", "")
                content = file.read_text(encoding="utf-8", errors="ignore")
                cleaned = clean_srt(content)
                extracted_sections.append(f"=== TRANSCRIPT: {title} ===\n{cleaned}\n")
            elif file.suffix == ".html" and "Description" in file.name:
                title = file.name.replace(" (Description).html", "").replace(".html", "")
                content = file.read_text(encoding="utf-8", errors="ignore")
                cleaned = clean_html(content)
                extracted_sections.append(f"=== DESCRIPTION: {title} ===\n{cleaned}\n")
            elif file.suffix == ".pdf":
                extracted_sections.append(f"=== NOTE: PDF file present: {file.name} ===\n[Please read PDF manually if needed]\n")
                
        if extracted_sections:
            output_file.write_text("\n".join(extracted_sections), encoding="utf-8")
            print(f"Saved consolidated text to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Extract transcripts and HTML descriptions from local structured courses")
    parser.add_argument("-i", "--input", required=True, help="Path to the course source directory containing subfolders/files")
    parser.add_argument("-o", "--output", help="Path to save the consolidated text files. Defaults to temp/extracted_text/{course_name}")
    args = parser.parse_args()
    
    source_path = Path(args.input)
    
    if args.output:
        output_path = Path(args.output)
    else:
        # Default output directory: project_root/temp/extracted_text/{course_folder_name}
        course_name = source_path.name
        project_root = Path(__file__).parent.parent
        output_path = project_root / "temp" / "extracted_text" / course_name
        
    extract_course(source_path, output_path)

if __name__ == "__main__":
    main()
