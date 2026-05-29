#!/usr/bin/env python3
"""
ytdlp_mcp — MCP server (stdio) para descargar transcripts de YouTube via yt-dlp.

Herramientas:
  - ytdlp_get_transcript        → transcript de un video individual
  - ytdlp_get_playlist          → transcripts de toda una playlist
  - ytdlp_list_playlist_videos  → lista los videos de una playlist sin descargar
"""

import json
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field, ConfigDict

# ---------------------------------------------------------------------------
# Server
# ---------------------------------------------------------------------------

mcp = FastMCP("ytdlp_mcp")

YTDLP_BIN = "yt-dlp" # Actualizado a usar la version del PATH o del entorno UV

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean_vtt(vtt_content: str) -> str:
    """Convierte un archivo VTT a texto plano limpio y deduplicado."""
    content = re.sub(r'WEBVTT\n.*?\n\n', '', vtt_content, flags=re.DOTALL)
    content = re.sub(
        r'\d{2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[.,]\d{3}[^\n]*\n',
        '', content
    )
    content = re.sub(r'<\d{2}:\d{2}:\d{2}\.\d{3}>', '', content)
    content = re.sub(r'<[^>]+>', '', content)
    content = re.sub(r'^\d+\s*$', '', content, flags=re.MULTILINE)
    lines = content.split('\n')
    seen, unique = set(), []
    for line in lines:
        line = line.strip()
        if line and line not in seen:
            seen.add(line)
            unique.append(line)
    return ' '.join(unique)


def _run_ytdlp_subtitles(url: str, lang: str, output_dir: Path) -> dict:
    """
    Ejecuta yt-dlp para descargar subtítulos.
    Retorna dict: {video_id: {title, url, transcript, lang_found}}
    """
    cmd = [
        YTDLP_BIN,
        '--write-auto-sub',
        '--write-sub',
        '--sub-lang', lang,
        '--sub-format', 'vtt',
        '--skip-download',
        '--no-playlist-reverse',
        '--print', '%(id)s|||%(title)s|||%(webpage_url)s',
        '--output', str(output_dir / '%(playlist_index)s-%(id)s.%(ext)s'),
        url
    ]

    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=str(output_dir), timeout=120
    )

    # Parsear info de los videos desde stdout
    videos = {}
    for line in result.stdout.strip().split('\n'):
        if '|||' in line:
            parts = line.split('|||')
            if len(parts) >= 2:
                vid_id = parts[0].strip()
                title = parts[1].strip()
                vid_url = parts[2].strip() if len(parts) > 2 else ''
                videos[vid_id] = {
                    'title': title,
                    'url': vid_url,
                    'transcript': '',
                    'lang_found': None,
                    'error': None
                }

    if not videos and result.returncode != 0:
        raise RuntimeError(f"yt-dlp falló: {result.stderr[:300]}")

    # Leer archivos VTT generados y asignar a cada video
    for vtt_file in output_dir.glob('*.vtt'):
        try:
            content = vtt_file.read_text(encoding='utf-8')
            clean = _clean_vtt(content)
            stem = vtt_file.stem  # ej: "1-KSItlTAsMsk.en"
            # Detectar lang del nombre del archivo
            lang_found = stem.split('.')[-1] if '.' in stem else lang
            # Buscar a qué video pertenece
            for vid_id in videos:
                if vid_id in stem:
                    videos[vid_id]['transcript'] = clean
                    videos[vid_id]['lang_found'] = lang_found
                    break
        except Exception as e:
            continue

    # Marcar videos sin transcript
    for vid_id, info in videos.items():
        if not info['transcript']:
            info['error'] = 'Transcript no disponible (video sin subtítulos o privado)'

    return videos


# ---------------------------------------------------------------------------
# Input models
# ---------------------------------------------------------------------------

class TranscriptInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    url: str = Field(
        ...,
        description="URL del video de YouTube. Ej: https://www.youtube.com/watch?v=KSItlTAsMsk",
        min_length=10
    )
    lang: str = Field(
        default='en',
        description="Código de idioma del subtítulo. Ej: 'en', 'es', 'fr'. Default: 'en'",
        min_length=2,
        max_length=10
    )


class PlaylistInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    url: str = Field(
        ...,
        description="URL de la playlist de YouTube. Ej: https://www.youtube.com/playlist?list=PL...",
        min_length=10
    )
    lang: str = Field(
        default='en',
        description="Código de idioma del subtítulo. Default: 'en'",
        min_length=2,
        max_length=10
    )
    max_videos: Optional[int] = Field(
        default=None,
        description="Número máximo de videos a procesar. None = todos. Útil para playlists grandes.",
        ge=1,
        le=200
    )


class ListPlaylistInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra='forbid')

    url: str = Field(
        ...,
        description="URL de la playlist de YouTube.",
        min_length=10
    )


# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@mcp.tool(
    name="ytdlp_get_transcript",
    annotations={
        "title": "Obtener transcript de un video de YouTube",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def ytdlp_get_transcript(params: TranscriptInput) -> str:
    """
    Descarga y retorna el transcript (subtítulos) de un video de YouTube.

    Usa yt-dlp para descargar subtítulos automáticos o manuales en el idioma
    especificado, limpia el formato VTT y retorna texto plano listo para procesar.

    Args:
        params (TranscriptInput):
            - url (str): URL del video de YouTube
            - lang (str): Código de idioma ('en', 'es', 'fr'...). Default: 'en'

    Returns:
        str: JSON con:
            - video_id (str): ID del video
            - title (str): Título del video
            - url (str): URL del video
            - lang (str): Idioma encontrado
            - transcript (str): Texto completo del transcript limpio
            - error (str|null): Mensaje de error si no hay transcript disponible
    """
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        try:
            videos = _run_ytdlp_subtitles(params.url, params.lang, tmp_path)
        except RuntimeError as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)

        if not videos:
            return json.dumps(
                {"error": f"No se encontró ningún video en: {params.url}"},
                ensure_ascii=False, indent=2
            )

        # Para un video individual, retornar el primero
        vid_id, info = next(iter(videos.items()))
        result = {
            "video_id": vid_id,
            "title": info['title'],
            "url": info['url'],
            "lang": info.get('lang_found') or params.lang,
            "transcript": info['transcript'],
            "char_count": len(info['transcript']),
            "error": info.get('error')
        }
        return json.dumps(result, ensure_ascii=False, indent=2)


@mcp.tool(
    name="ytdlp_get_playlist",
    annotations={
        "title": "Obtener transcripts de una playlist completa de YouTube",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def ytdlp_get_playlist(params: PlaylistInput) -> str:
    """
    Descarga y retorna los transcripts de todos los videos de una playlist de YouTube.

    Procesa cada video de la playlist en orden, descargando sus subtítulos automáticos
    o manuales. Ideal para procesar cursos, series o colecciones de videos completas.

    Args:
        params (PlaylistInput):
            - url (str): URL de la playlist de YouTube
            - lang (str): Código de idioma. Default: 'en'
            - max_videos (int|None): Límite de videos a procesar. None = todos.

    Returns:
        str: JSON con:
            - playlist_url (str): URL de la playlist procesada
            - total_videos (int): Total de videos procesados
            - lang (str): Idioma solicitado
            - videos (list): Lista de objetos con video_id, title, url, transcript, error
            - summary (dict): Estadísticas: total, con_transcript, sin_transcript
    """
    # Aplicar límite si se especificó
    url = params.url
    if params.max_videos:
        # yt-dlp acepta --playlist-end para limitar
        cmd_extra = ['--playlist-end', str(params.max_videos)]
    else:
        cmd_extra = []

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        try:
            if cmd_extra:
                # Inyectar flags extra antes de la URL
                import shlex
                # Usamos subprocess directo para pasar flags adicionales
                cmd = [
                    YTDLP_BIN,
                    '--write-auto-sub', '--write-sub',
                    '--sub-lang', params.lang,
                    '--sub-format', 'vtt',
                    '--skip-download',
                    '--no-playlist-reverse',
                    '--print', '%(id)s|||%(title)s|||%(webpage_url)s',
                    '--output', str(tmp_path / '%(playlist_index)s-%(id)s.%(ext)s'),
                ] + cmd_extra + [url]

                result = subprocess.run(
                    cmd, capture_output=True, text=True,
                    cwd=str(tmp_path), timeout=300
                )

                videos = {}
                for line in result.stdout.strip().split('\n'):
                    if '|||' in line:
                        parts = line.split('|||')
                        vid_id = parts[0].strip()
                        title = parts[1].strip() if len(parts) > 1 else ''
                        vid_url = parts[2].strip() if len(parts) > 2 else ''
                        videos[vid_id] = {
                            'title': title, 'url': vid_url,
                            'transcript': '', 'lang_found': None, 'error': None
                        }

                for vtt_file in tmp_path.glob('*.vtt'):
                    try:
                        content = vtt_file.read_text(encoding='utf-8')
                        clean = _clean_vtt(content)
                        stem = vtt_file.stem
                        lang_found = stem.split('.')[-1] if '.' in stem else params.lang
                        for vid_id in videos:
                            if vid_id in stem:
                                videos[vid_id]['transcript'] = clean
                                videos[vid_id]['lang_found'] = lang_found
                                break
                    except Exception:
                        continue

                for vid_id, info in videos.items():
                    if not info['transcript']:
                        info['error'] = 'Transcript no disponible'
            else:
                videos = _run_ytdlp_subtitles(url, params.lang, tmp_path)

        except RuntimeError as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False, indent=2)

        video_list = []
        for vid_id, info in videos.items():
            video_list.append({
                "video_id": vid_id,
                "title": info['title'],
                "url": info['url'],
                "lang": info.get('lang_found') or params.lang,
                "transcript": info['transcript'],
                "char_count": len(info['transcript']),
                "error": info.get('error')
            })

        con_transcript = sum(1 for v in video_list if v['transcript'])
        sin_transcript = len(video_list) - con_transcript

        response = {
            "playlist_url": url,
            "total_videos": len(video_list),
            "lang": params.lang,
            "videos": video_list,
            "summary": {
                "total": len(video_list),
                "con_transcript": con_transcript,
                "sin_transcript": sin_transcript
            }
        }
        return json.dumps(response, ensure_ascii=False, indent=2)


@mcp.tool(
    name="ytdlp_list_playlist_videos",
    annotations={
        "title": "Listar videos de una playlist sin descargar transcripts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def ytdlp_list_playlist_videos(params: ListPlaylistInput) -> str:
    """
    Lista los videos de una playlist de YouTube sin descargar subtítulos.

    Útil para explorar el contenido de una playlist antes de decidir qué
    videos procesar con ytdlp_get_transcript o ytdlp_get_playlist.

    Args:
        params (ListPlaylistInput):
            - url (str): URL de la playlist de YouTube

    Returns:
        str: JSON con:
            - playlist_url (str): URL de la playlist
            - total_videos (int): Número total de videos
            - videos (list): Lista con index, video_id, title, url de cada video
    """
    cmd = [
        YTDLP_BIN,
        '--flat-playlist',
        '--print', '%(playlist_index)s|||%(id)s|||%(title)s|||%(webpage_url)s',
        params.url
    ]

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0 and not result.stdout:
        return json.dumps(
            {"error": f"Error al listar playlist: {result.stderr[:300]}"},
            ensure_ascii=False, indent=2
        )

    videos = []
    for line in result.stdout.strip().split('\n'):
        if '|||' in line:
            parts = line.split('|||')
            if len(parts) >= 3:
                videos.append({
                    "index": parts[0].strip(),
                    "video_id": parts[1].strip(),
                    "title": parts[2].strip(),
                    "url": parts[3].strip() if len(parts) > 3 else f"https://youtu.be/{parts[1].strip()}"
                })

    return json.dumps({
        "playlist_url": params.url,
        "total_videos": len(videos),
        "videos": videos
    }, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()  # stdio transport por defecto
