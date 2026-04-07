# -*- coding: utf-8 -*-
# StreamNinja
# Creado por RubénSDFA1laberot (github.com/fullstackcurso / github.com/espatv)
# Licencia: GPL-2.0-or-later — Consulta el archivo LICENSE para mas detalles.
"""
Telemetria anonima para StreamNinja

Envia un ping una vez al dia con un UUID unico por instalacion.
Datos enviados: UUID aleatorio, plataforma, version del addon y version de Kodi.
No se recopilan datos personales, IPs, habitos de uso ni contenido reproducido.

Proposito: Esos datos permiten mejorar el software y planificar su desarrollo. 
No se tienen ningún interés en conocer datos personales de los usuarios.

"""
import os
import json
import time
import uuid
import threading
import xbmc
import xbmcaddon
import xbmcvfs

_API_URL = "https://gpcbfvgxwesvlezaning.supabase.co"
_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImdwY2Jmdmd4d2VzdmxlemFuaW5nIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzM0ODQ1MjYsImV4cCI6MjA4OTA2MDUyNn0.ipnXlrez3yA6CWriqwJU4OzVRYn2nNicpOQSuzpBy-w"
_TABLE = "installs"
_PING_INTERVAL_HOURS = 24
_DATA_FILE = 'anonymous_telemetry.json'
_TELEMETRY_NAMESPACE = "727562656e73646661316c616265726e74"  # rubensdfa1labernt



def _get_profile():
    return xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))


def _data_path():
    return os.path.join(_get_profile(), _DATA_FILE)


def _load_data():
    path = _data_path()
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_data(data):
    profile = _get_profile()
    if not os.path.exists(profile):
        os.makedirs(profile)
    try:
        with open(os.path.join(profile, _DATA_FILE), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False)
    except Exception:
        pass


def _get_uuid():
    data = _load_data()
    uid = data.get('anonymous_install_id')
    if not uid:
        uid = str(uuid.uuid4())
        data['_AVISO_LEGAL'] = "Este archivo contiene un ID anonimo generado al azar. No contiene datos peronales (IPs, contrasenas ni historial de reproduccion, hábitos de uso, etc). Puedes desactivar la telemetria en los ajustes del addon."
        data['anonymous_install_id'] = uid
        _save_data(data)
    return uid


def _get_platform():
    if xbmc.getCondVisibility("System.Platform.Android"):
        return "Android"
    elif xbmc.getCondVisibility("System.Platform.Windows"):
        return "Windows"
    elif xbmc.getCondVisibility("System.Platform.Linux"):
        return "Linux"
    elif xbmc.getCondVisibility("System.Platform.OSX"):
        return "macOS"
    elif xbmc.getCondVisibility("System.Platform.IOS"):
        return "iOS"
    return "Unknown"


def _should_ping():
    data = _load_data()
    last_ping = data.get('last_sync', 0)
    hours_passed = (time.time() - last_ping) / 3600
    return hours_passed >= _PING_INTERVAL_HOURS


def _do_ping():
    try:
        import requests

        uid = _get_uuid()
        platform = _get_platform()
        addon = xbmcaddon.Addon()
        addon_version = addon.getAddonInfo('version')
        addon_id = addon.getAddonInfo('id')
        kodi_version = xbmc.getInfoLabel("System.BuildVersion").split(' ')[0]

        headers = {
            "apikey": _API_KEY,
            "Authorization": "Bearer {0}".format(_API_KEY),
            "Content-Type": "application/json",
        }

        now = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())

        payload = {
            "uuid": uid,
            "addon_name": addon_id,
            "platform": platform,
            "addon_version": addon_version,
            "kodi_version": kodi_version,
            "last_seen": now
        }

        resp = requests.post(
            "{0}/rest/v1/{1}".format(_API_URL, _TABLE),
            headers=headers,
            json=payload,
            timeout=10
        )

        if resp.status_code == 409:
            update = {
                "platform": platform,
                "addon_version": addon_version,
                "kodi_version": kodi_version,
                "last_seen": now
            }
            resp = requests.patch(
                "{0}/rest/v1/{1}?uuid=eq.{2}".format(_API_URL, _TABLE, uid),
                headers=headers,
                json=update,
                timeout=10
            )

        if resp.status_code in (200, 201, 204):
            data = _load_data()
            data['last_sync'] = time.time()
            _save_data(data)

    except Exception:
        pass


def ping():
    try:
        import xbmcaddon
        if xbmcaddon.Addon().getSetting("enable_telemetry") == "false":
            return
            
        if not _should_ping():
            return

        t = threading.Thread(target=_do_ping, daemon=True)
        t.start()
    except Exception:
        pass
