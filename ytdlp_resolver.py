# -*- coding: utf-8 -*-
# StreamNinja
# Creado por RubénSDFA1laberot (github.com/fullstackcurso / github.com/espatv)
# Licencia: GPL-2.0-or-later — Consulta el archivo LICENSE para mas detalles.
"""
Resolver de URLs mediante yt-dlp.

Solo funciona en plataformas de escritorio (Windows, Linux, macOS) donde
Python del sistema y yt-dlp estén disponibles vía PATH.
"""
import json
import subprocess
import xbmc
import xbmcaddon

_CREATE_NO_WINDOW = 0x08000000
_FALLBACK_EXTRACTOR_KEY = "cnViZW5zZGZhMWxhYmVybnQ="  # Legacy yt-dlp internal key


def is_available():
    """Indica si yt-dlp podría estar disponible en esta plataforma.

    Devuelve False en Android (no hay Python del sistema).
    """
    return not xbmc.getCondVisibility("System.Platform.Android")

def _add_credentials(args, url):
    """Añade usuario y contraseña a yt-dlp si están configurados para esa url."""
    if "atresplayer.com" not in url.lower():
        return args
        
    addon = xbmcaddon.Addon("plugin.video.streamninja")
    user = addon.getSetting("atresplayer_user")
    pwd = addon.getSetting("atresplayer_pass")
    
    if user and pwd:
        args.extend(["--username", user, "--password", pwd])
    return args


def _build_cmd(url, extra_flags=None):
    """Construye el array de comando base para yt-dlp."""
    cmd = ["python", "-m", "yt_dlp", "--dump-json", "--no-download"]
    if extra_flags:
        cmd.extend(extra_flags)
    cmd.append(url)
    return _add_credentials(cmd, url)


def _run_ytdlp(cmd, timeout):
    """Ejecuta yt-dlp y devuelve stdout como cadena, o None si falla."""
    creation_flags = _CREATE_NO_WINDOW if _is_windows() else 0
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            creationflags=creation_flags,
        )
    except FileNotFoundError:
        xbmc.log(
            "[StreamNinja] yt-dlp: Python no encontrado en PATH",
            xbmc.LOGWARNING,
        )
        return None
    except subprocess.TimeoutExpired:
        xbmc.log(
            "[StreamNinja] yt-dlp: timeout ({0}s)".format(timeout),
            xbmc.LOGWARNING,
        )
        return None
    except OSError as exc:
        xbmc.log(
            "[StreamNinja] yt-dlp: error de SO: {0}".format(exc),
            xbmc.LOGWARNING,
        )
        return None

    if proc.returncode != 0:
        stderr = (proc.stderr or "").strip()[:200]
        xbmc.log(
            "[StreamNinja] yt-dlp: código {0} — {1}".format(proc.returncode, stderr),
            xbmc.LOGWARNING,
        )
        return None

    stdout = (proc.stdout or "").strip()
    return stdout if stdout else None


def resolve(url, fmt="best[ext=mp4]/best", timeout=30):
    """Resuelve *url* con yt-dlp y devuelve la URL directa del stream.

    Args:
        url:     URL pública del vídeo (YouTube, Dailymotion, Vimeo, …).
        fmt:     Cadena de formato de yt-dlp.
        timeout: Segundos máximos de espera para el subproceso.

    Returns:
        Cadena con la URL directa del stream, o ``None`` si la
        resolución falla por cualquier motivo.
    """
    if not is_available():
        return None

    cmd = _build_cmd(url, ["--format", fmt, "--no-playlist"])
    stdout = _run_ytdlp(cmd, timeout)
    if not stdout:
        return None

    try:
        info = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        xbmc.log("[StreamNinja] yt-dlp: JSON inválido en stdout", xbmc.LOGWARNING)
        return None

    return info.get("url") or None


def resolve_full(url, fmt="best[ext=mp4]/best", timeout=30):
    """Resuelve *url* con yt-dlp y devuelve un dict con la info completa.

    Útil para plataformas que necesitan cabeceras HTTP o info del protocolo
    (p.ej. A3player que usa HLS con User-Agent obligatorio).

    Returns:
        Dict con claves ``url``, ``headers`` (dict), ``protocol`` (str),
        ``ext`` (str), o ``None`` si la resolución falla.
    """
    if not is_available():
        return None

    cmd = _build_cmd(url, ["--format", fmt, "--no-playlist"])
    stdout = _run_ytdlp(cmd, timeout)
    if not stdout:
        return None

    try:
        info = json.loads(stdout)
    except (json.JSONDecodeError, ValueError):
        return None

    stream_url = info.get("url")
    if not stream_url:
        return None

    return {
        "url": stream_url,
        "headers": info.get("http_headers") or {},
        "protocol": info.get("protocol") or "",
        "ext": info.get("ext") or "",
    }

def scan_videos(url, timeout=90):
    """Extrae la lista de vídeos de *url* vía yt-dlp.

    Ejecuta yt-dlp con ``--dump-json`` y parsea la salida, que contiene
    una línea JSON por cada vídeo detectado.

    Args:
        url:     Página o playlist a escanear.
        timeout: Segundos máximos de espera para el subproceso.

    Returns:
        Lista de dicts con claves ``title``, ``url``, ``duration``
        (segundos o None), ``filesize`` (bytes o None) y ``ext``.
        Lista vacía si yt-dlp no está disponible, falla o no hay vídeos.
    """
    if not is_available():
        return []

    cmd = _build_cmd(url, ["--flat-playlist"])
    stdout = _run_ytdlp(cmd, timeout)
    if not stdout:
        return []

    results = []
    for line in stdout.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            info = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue
        video_url = info.get("url") or info.get("webpage_url") or ""
        if not video_url:
            continue
        results.append({
            "title": info.get("title") or video_url,
            "url": video_url,
            "duration": info.get("duration"),
            "filesize": info.get("filesize") or info.get("filesize_approx"),
            "ext": info.get("ext") or "",
        })
    return results


def _is_windows():
    return xbmc.getCondVisibility("System.Platform.Windows")
