#!/usr/bin/env python3
import os
import sys
import json
import argparse
import time
import requests
from pathlib import Path

# Add project root and scripts directory to python path
PROJECT_DIR = Path(__file__).parent.parent
sys.path.append(str(PROJECT_DIR / "scripts"))

# Load environment variables
def load_env():
    env_path = PROJECT_DIR / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                val = val.strip().strip('"').strip("'")
                os.environ[key.strip()] = val

load_env()
raw_gemini_key = os.environ.get("GEMINI_API_KEY", "")
if not raw_gemini_key or "your-gemini-api-key" in raw_gemini_key:
    GEMINI_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
else:
    GEMINI_API_KEY = raw_gemini_key
raw_engine = os.environ.get("MODEL_ENGINE", "gemini-2.5-flash")
MODEL_ENGINE = "gemini-2.5-flash" if "gemini-3.1-pro" in raw_engine or not raw_engine else raw_engine

# Ollama hybrid configuration
DENSITY_GRADER_PROVIDER = os.environ.get("DENSITY_GRADER_PROVIDER", "gemini").strip().lower()
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434").strip()
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2").strip()

def grade_density_via_gemini(text_snippet: str, max_retries=5) -> dict:
    """Grades the technical density of the text snippet using Gemini."""
    if not GEMINI_API_KEY or "your-gemini-api-key" in GEMINI_API_KEY:
        print("[Grader Error] GEMINI_API_KEY is not configured.", file=sys.stderr)
        return {
            "score": 1.0, 
            "reason": "GEMINI_API_KEY not configured in .env. Evaluation skipped, defaulting to 1.0."
        }
        
    prompt = f"""
Act as a Senior AI Engineer and Technical Editor. Evaluate the technical density of the following text snippet.
Technical density measures the concentration of concrete technical explanations, system design architectures, algorithms, equations, code patterns, or API specifications, vs marketing fluff, introductory boilerplate, generic tutorials (e.g. "how to install python"), or high-level non-technical descriptions.

Evaluate based on:
1. Depth of explanations (explaining "how it works under the hood" vs "what it is").
2. Presence of concrete code blocks, mathematical equations, system architecture diagrams represented as text, or precise API signatures.
3. Noise-to-signal ratio (boilerplates, sponsor segments, ads).
4. Target audience (is it aimed at advanced/intermediate developers or complete beginners/marketing audiences?).

Format your output strictly as a JSON object with two keys:
- "score": A float between 0.0 (zero technical value, pure fluff/marketing/basics) and 1.0 (highly advanced, code/formula/architecture dense, academic paper/technical spec level).
- "reason": A brief one-to-two sentence explanation of the score in the language of the text snippet.

Text Snippet to Grade:
---
{text_snippet[:4000]}
---

Do not output markdown code blocks like ```json. Output only the raw JSON object.
"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL_ENGINE}:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.1
        }
    }
    
    delay = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 429:
                time.sleep(delay)
                delay *= 2
                continue
            if response.status_code != 200:
                print(f"[Grader Error] API Response details: {response.text}", file=sys.stderr)
            response.raise_for_status()
            res_json = response.json()
            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            
            # Clean JSON just in case the model ignored responseMimeType
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[Grader Error] Failed to contact Gemini API: {e}", file=sys.stderr)
                return {"score": 1.0, "reason": f"API call failed: {e}. Defaulted to 1.0."}
            time.sleep(delay)
            delay *= 2
            
    return {"score": 1.0, "reason": "Grading timed out, defaulted to 1.0."}

def grade_density_via_ollama(text_snippet: str, host: str = None, model: str = None, max_retries=3) -> dict:
    """Grades the technical density of the text snippet using Ollama."""
    host = (host or OLLAMA_HOST).rstrip("/")
    model = model or OLLAMA_MODEL
    
    prompt = f"""
Act as a Senior AI Engineer and Technical Editor. Evaluate the technical density of the following text snippet.
Technical density measures the concentration of concrete technical explanations, system design architectures, algorithms, equations, code patterns, or API specifications, vs marketing fluff, introductory boilerplate, generic tutorials (e.g. "how to install python"), or high-level non-technical descriptions.

Evaluate based on:
1. Depth of explanations (explaining "how it works under the hood" vs "what it is").
2. Presence of concrete code blocks, mathematical equations, system architecture diagrams represented as text, or precise API signatures.
3. Noise-to-signal ratio (boilerplates, sponsor segments, ads).
4. Target audience (is it aimed at advanced/intermediate developers or complete beginners/marketing audiences?).

Format your output strictly as a JSON object with two keys:
- "score": A float between 0.0 (zero technical value, pure fluff/marketing/basics) and 1.0 (highly advanced, code/formula/architecture dense, academic paper/technical spec level).
- "reason": A brief one-to-two sentence explanation of the score in the language of the text snippet.

Text Snippet to Grade:
---
{text_snippet[:4000]}
---

Do not output markdown code blocks. Output only the raw JSON object.
"""
    
    url = f"{host}/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.1
        }
    }
    
    delay = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, timeout=60)
            if response.status_code != 200:
                print(f"[Grader Error] Ollama Response details: {response.text}", file=sys.stderr)
            response.raise_for_status()
            res_json = response.json()
            raw_text = res_json["response"].strip()
            
            clean_json = raw_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            if attempt == max_retries - 1:
                print(f"[Grader Error] Failed to contact Ollama API: {e}", file=sys.stderr)
                raise e
            time.sleep(delay)
            delay *= 2

def grade_technical_density(text_snippet: str, provider: str = None, host: str = None, model: str = None, max_retries=5) -> dict:
    """
    Grades the technical density of the text snippet using either Gemini or Ollama.
    Returns a dict: {"score": float, "reason": str}
    """
    active_provider = (provider or DENSITY_GRADER_PROVIDER).strip().lower()
    
    if active_provider == "ollama":
        try:
            print(f"[Grader] Using Ollama provider at {host or OLLAMA_HOST} with model {model or OLLAMA_MODEL}")
            return grade_density_via_ollama(text_snippet, host=host, model=model, max_retries=3)
        except Exception as e:
            print(f"[Grader Warning] Ollama density grading failed: {e}. Falling back to Gemini...", file=sys.stderr)
            # Fall back to Gemini
            return grade_density_via_gemini(text_snippet, max_retries=max_retries)
    else:
        # Default to Gemini
        return grade_density_via_gemini(text_snippet, max_retries=max_retries)

def main():
    parser = argparse.ArgumentParser(description="Evaluate technical density of a document")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="Path to markdown or text file")
    group.add_argument("--text", help="Raw text to grade")
    parser.add_argument("--provider", choices=["gemini", "ollama"], help="LLM Provider to use (overrides DENSITY_GRADER_PROVIDER)")
    parser.add_argument("--ollama-host", help="Ollama host URL (overrides OLLAMA_HOST)")
    parser.add_argument("--ollama-model", help="Ollama model name (overrides OLLAMA_MODEL)")
    
    args = parser.parse_args()
    
    text = ""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: File not found {file_path}")
            sys.exit(1)
        text = file_path.read_text(encoding="utf-8")
    else:
        text = args.text
        
    result = grade_technical_density(
        text,
        provider=args.provider,
        host=args.ollama_host,
        model=args.ollama_model
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
