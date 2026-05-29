"""
yt_transcript_mcp - MCP Server local para descargar y limpiar transcripts de YouTube.

Expone dos tools:
  - yt_get_transcript : descarga y limpia el transcript de una URL de YouTube
  - yt_list_transcripts: lista los transcripts ya guardados en el directorio local

Transporte: stdio (para Claude Desktop)
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
# CONFIGURACIÓN
# =============================================================================

# Directorio base donde se guardan los transcripts
TRANSCRIPTS_DIR = Path("/Users/carlosibarra/Downloads/yt-transcripts")

# Idiomas preferidos (en orden de prioridad)
PREFERRED_LANGS = ["es", "en"]

# =============================================================================
# INICIALIZACIÓN DEL SERVIDOR
# =============================================================================

mcp = FastMCP("yt_transcript_mcp")

# =============================================================================
# HELPERS
# =============================================================================

def to_camel_case(text: str) -> str:
    """Convierte un texto a camelCase eliminando caracteres especiales."""
    # Normalizar: minúsculas y reemplazar caracteres no ASCII
    text = text.lower()
    # Reemplazar caracteres especiales comunes
    replacements = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n", "ç": "c",
    }
    for original, replacement in replacements.items():
        text = text.replace(original, replacement)

    # Eliminar caracteres que no sean letras, números o espacios
    text = re.sub(r"[^a-z0-9 ]", "", text)

    # Convertir a camelCase
    words = text.split()
    if not words:
        return "videoTranscript"
    return words[0] + "".join(w.capitalize() for w in words[1:])


def clean_vtt_content(vtt_text: str) -> str:
    """
    Limpia el contenido de un archivo .vtt y devuelve texto plano legible.
    Elimina: timestamps, cabeceras, etiquetas HTML, duplicados consecutivos.
    """
    lines = vtt_text.splitlines()
    clean_lines = []

    for line in lines:
        # Eliminar cabecera WEBVTT y metadatos
        if re.match(r"^(WEBVTT|Kind:|Language:)", line.strip()):
            continue
        # Eliminar timestamps (00:00:01.000 --> 00:00:03.000)
        if re.match(r"^\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*", line):
            continue
        # Eliminar numeración sola
        if re.match(r"^\d+$", line.strip()):
            continue
        # Eliminar etiquetas HTML (<c>, </c>, <00:00:01.000>, etc.)
        line = re.sub(r"<[^>]+>", "", line)
        # Saltar líneas vacías
        if not line.strip():
            continue
        clean_lines.append(line.strip())

    # Eliminar líneas duplicadas consecutivas
    deduped = []
    prev = None
    for line in clean_lines:
        if line != prev:
            deduped.append(line)
        prev = line

    return " ".join(deduped)


def find_vtt_file(directory: Path) -> Optional[Path]:
    """
    Busca el archivo .vtt en un directorio, priorizando español sobre inglés.
    """
    for lang in PREFERRED_LANGS:
        matches = list(directory.glob(f"*.{lang}.vtt"))
        if matches:
            return matches[0]
    # Fallback: cualquier .vtt
    all_vtt = list(directory.glob("*.vtt"))
    return all_vtt[0] if all_vtt else None


def get_video_title(url: str) -> str:
    """Obtiene el título del video usando yt-dlp."""
    result = subprocess.run(
        ["yt-dlp", "--get-title", "--no-warnings", "--cookies-from-browser", "chrome", url],
        capture_output=True,
        text=True,
        timeout=30,
    )
    if result.returncode != 0:
        raise RuntimeError(f"No se pudo obtener el título: {result.stderr.strip()}")
    return result.stdout.strip()


def download_vtt(url: str, output_dir: Path) -> None:
    """Descarga el archivo .vtt del video con yt-dlp."""
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
        raise RuntimeError(f"yt-dlp falló: {result.stderr.strip()}")

# =============================================================================
# MODELOS PYDANTIC
# =============================================================================

class GetTranscriptInput(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid",
    )

    url: str = Field(
        ...,
        description="URL del video de YouTube (ej: 'https://www.youtube.com/watch?v=XXXXX')",
        min_length=10,
    )
    title: Optional[str] = Field(
        default=None,
        description="Título del video (opcional). Si no se provee, se obtiene automáticamente.",
        max_length=200,
    )
    save_file: bool = Field(
        default=True,
        description="Si True, guarda el transcript como .txt en ~/Downloads/yt-transcripts/<camelCase>/",
    )


class ListTranscriptsInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    limit: int = Field(
        default=20,
        description="Máximo de transcripts a listar",
        ge=1,
        le=100,
    )

# =============================================================================
# TOOLS
# =============================================================================

@mcp.tool(
    name="yt_get_transcript",
    annotations={
        "title": "Descargar y limpiar transcript de YouTube",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
async def yt_get_transcript(params: GetTranscriptInput) -> str:
    """
    Descarga el transcript (subtítulos) de un video de YouTube, lo limpia
    y opcionalmente lo guarda como archivo .txt.

    Proceso:
    1. Obtiene el título del video (o usa el provisto)
    2. Descarga el .vtt con yt-dlp (prefiere español sobre inglés)
    3. Limpia timestamps, etiquetas HTML y duplicados
    4. Guarda en ~/Downloads/yt-transcripts/<camelCase>/<camelCase>.txt

    Args:
        params (GetTranscriptInput):
            - url (str): URL del video de YouTube
            - title (Optional[str]): Título manual (evita llamada extra a yt-dlp)
            - save_file (bool): Si guardar el .txt localmente (default: True)

    Returns:
        str: JSON con campos:
            - success (bool)
            - title (str): Título del video
            - folder_name (str): Nombre camelCase usado para la carpeta
            - output_path (str): Ruta del archivo guardado (si save_file=True)
            - transcript (str): Texto limpio del transcript
            - word_count (int): Cantidad de palabras
            - error (str): Mensaje de error si success=False
    """
    tmp_dir = None
    try:
        # --- Paso 1: Obtener título ---
        if params.title:
            video_title = params.title
        else:
            video_title = get_video_title(params.url)

        folder_name = to_camel_case(video_title) or "videoTranscript"

        # --- Paso 2: Descargar .vtt en directorio temporal ---
        tmp_dir = Path(tempfile.mkdtemp(prefix="yt_mcp_"))
        download_vtt(params.url, tmp_dir)

        # --- Paso 3: Encontrar y leer el .vtt ---
        vtt_file = find_vtt_file(tmp_dir)
        if not vtt_file:
            return json.dumps({
                "success": False,
                "error": "No se encontró archivo .vtt. El video puede no tener subtítulos disponibles.",
            })

        vtt_text = vtt_file.read_text(encoding="utf-8")

        # --- Paso 4: Limpiar el transcript ---
        clean_text = clean_vtt_content(vtt_text)
        if not clean_text.strip():
            return json.dumps({
                "success": False,
                "error": "El transcript quedó vacío después de la limpieza.",
            })

        # --- Paso 5: Guardar como .txt (opcional) ---
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
        return json.dumps({"success": False, "error": "Timeout al ejecutar yt-dlp. Verificá tu conexión."})
    except RuntimeError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Error inesperado: {type(e).__name__}: {e}"})
    finally:
        # Limpiar directorio temporal siempre
        if tmp_dir and tmp_dir.exists():
            shutil.rmtree(tmp_dir, ignore_errors=True)


@mcp.tool(
    name="yt_list_transcripts",
    annotations={
        "title": "Listar transcripts guardados",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def yt_list_transcripts(params: ListTranscriptsInput) -> str:
    """
    Lista los transcripts ya guardados en ~/Downloads/yt-transcripts/.

    Args:
        params (ListTranscriptsInput):
            - limit (int): Máximo de resultados a devolver (default: 20)

    Returns:
        str: JSON con campos:
            - success (bool)
            - base_dir (str): Directorio base de transcripts
            - total (int): Total de transcripts encontrados
            - transcripts (list): Lista con name, path, size_kb, word_count
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
    # Transporte stdio — Claude Desktop gestiona el proceso
    mcp.run()
