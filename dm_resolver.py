# -*- coding: utf-8 -*-
# StreamNinja
# Creado por RubénSDFA1laberot (github.com/fullstackcurso / github.com/espatv)
# Licencia: GPL-2.0-or-later — Consulta el archivo LICENSE para mas detalles.
"""
Resolutor de Dailymotion para StreamNinja.
"""
import re
from urllib.parse import quote, urljoin
import xbmc
try:
    import requests
except ImportError:
    requests = None

_HEADERS_DM_DESKTOP = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Origin": "https://www.dailymotion.com",
    "Referer": "https://www.dailymotion.com/",
    "X-Client-Signature": "cnViZW5zZGZhMWxhYmVybnQ="
}

def _log_error(msg):
    xbmc.log("[StreamNinja] " + str(msg), xbmc.LOGERROR)

def _fetch_hls_variants(master_url, headers=None):
    """Descarga un master playlist HLS y devuelve las variantes ordenadas por ancho de banda."""
    if not requests:
        return []
    variants = []
    req_headers = headers if headers else {}
    try:
        r = requests.get(master_url, headers=req_headers, timeout=15)
        if r.status_code != 200:
            return variants
            
        lines = r.text.strip().splitlines()
        
        current_label = "unknown"
        current_bw = 0
        expecting_url = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('#EXT-X-STREAM-INF'):
                res_match = re.search(r'RESOLUTION=(\d+x\d+)', line)
                bw_match = re.search(r'BANDWIDTH=(\d+)', line)
                current_label = res_match.group(1) if res_match else "unknown"
                current_bw = int(bw_match.group(1)) if bw_match else 0
                expecting_url = True
            elif expecting_url and not line.startswith('#'):
                stream_url = line
                if not stream_url.startswith('http'):
                    stream_url = urljoin(master_url, stream_url)
                variants.append({'label': current_label, 'url': stream_url, 'bandwidth': current_bw})
                expecting_url = False
                
        variants.sort(key=lambda x: x.get('bandwidth', 0), reverse=True)
    except Exception as exc:
        _log_error("HLS variants lookup error: {0}".format(exc))
    return variants


def _dm_play_direct(vid, max_quality=1080):
    if not requests:
        return None
    if not isinstance(vid, str) or not vid.strip():
        return None
        
    vid_safe = quote(vid.strip())
    try:
        meta_url = "https://www.dailymotion.com/player/metadata/video/{0}".format(vid_safe)
        r = requests.get(meta_url, headers=_HEADERS_DM_DESKTOP, timeout=15)
        if r.status_code != 200:
            return None
            
        data = r.json()
        if data.get("error"):
            return None

        qualities = data.get("qualities", {})
        subtitles = []
        subs_data = data.get("subtitles", {})
        if isinstance(subs_data, dict):
            for lang, sub_list in subs_data.items():
                if isinstance(sub_list, list):
                    for sub in sub_list:
                        if isinstance(sub, dict) and sub.get("url"):
                            subtitles.append(sub.get("url"))

        best_mp4 = None
        best_res = 0
        for res_key, formats in qualities.items():
            if res_key == "auto":
                continue
            try:
                res_val = int(res_key)
            except (ValueError, TypeError):
                continue
                
            if res_val > max_quality:
                continue
                
            for fmt in formats:
                if isinstance(fmt, dict) and fmt.get("type") == "video/mp4" and res_val > best_res:
                    best_mp4 = fmt.get("url")
                    best_res = res_val
                    
        if best_mp4:
            return {"url": best_mp4, "mime": "video/mp4", "subs": subtitles, "headers": _HEADERS_DM_DESKTOP}

        hls_url = None
        if "auto" in qualities:
            for item in qualities["auto"]:
                if isinstance(item, dict) and item.get("type") == "application/x-mpegURL":
                    hls_url = item.get("url")
                    break
                    
        if hls_url:
            variants = _fetch_hls_variants(hls_url, headers=_HEADERS_DM_DESKTOP)
            if variants:
                filtered = []
                for v in variants:
                    label = v.get("label", "")
                    try:
                        height = int(label.split("x")[1].split(" ")[0]) if "x" in label else 0
                    except (ValueError, IndexError):
                        height = 0
                    if height > 0 and height <= max_quality:
                        filtered.append(v)
                target = filtered[0] if filtered else variants[-1]
                return {"url": target["url"], "mime": "application/x-mpegURL", "subs": subtitles, "headers": _HEADERS_DM_DESKTOP}
            return {"url": hls_url, "mime": "application/x-mpegURL", "subs": subtitles, "headers": _HEADERS_DM_DESKTOP}
    except Exception as exc:
        _log_error("_dm_play_direct error: {0}".format(exc))
    return None

def _dm_play(vid, dm_level=0, max_quality=1080):
    try:
        import dm_gujal
        if dm_level == 2:
            url, subs, mime = dm_gujal.play_dm_extreme(vid, max_quality=max_quality)
            if url: return {'url': url, 'subs': subs, 'mime': mime or 'application/x-mpegURL'}
        elif dm_level == 1:
            url, mime = dm_gujal.play_dm_basic(vid)
            if url: return {'url': url, 'mime': mime or 'application/x-mpegURL'}
        else:
            url, subs, mime = dm_gujal.play_dm_extreme(vid, max_quality=max_quality)
            if url: return {'url': url, 'subs': subs, 'mime': mime or 'application/x-mpegURL'}
            url, mime = dm_gujal.play_dm_basic(vid)
            if url: return {'url': url, 'mime': mime or 'application/x-mpegURL'}
    except Exception as exc:
        _log_error("dm_gujal play error: {0}".format(exc))

    result = _dm_play_direct(vid, max_quality=max_quality)
    if result:
        return result
    return None

def _dm_play_android(vid, dm_level=0, max_quality=1080):
    result = _dm_play_direct(vid, max_quality=max_quality)
    if not result or not result.get('url'):
        result = _dm_play(vid, dm_level=dm_level, max_quality=max_quality)

    if result is None:
        return None

    result.pop('headers', None)
    return result

