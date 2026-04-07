# -*- coding: utf-8 -*-
# StreamNinja
# Creado por RubénSDFA1laberot (github.com/fullstackcurso)
# Licencia: GPL-2.0-or-later — Consulta el archivo LICENSE para mas detalles.
#
# ESTREAMNINJA EXPERIMENTAL:
# EstreamNinja es una versión experimental donde se prueban funcionalidades que puede que lleguen a StreamNinja o no.
# Y además tiene la peculiaridad de que está todo en español, que es el idioma nativo de RubénSDFA1laberot,
# para facilitar el desarrollo. Esta versión no está pensada para ser usada por usuarios finales ni por desarrolladores,
# ya que ni siquiera se ha comentado el código como es debido. Y hay mucho código que no se usa ni está pulido.
"""
Modulo de informacion del addon.

Gestiona el submenu de informacion, el aviso legal
y la descarga en segundo plano de recursos graficos
para el dialogo Universo.
"""
import sys
import os
import threading
import urllib.parse
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon
import xbmcvfs


def _u(**kwargs):
    return sys.argv[0] + "?" + urllib.parse.urlencode(kwargs)


def _get_handle():
    try:
        return int(sys.argv[1])
    except (IndexError, ValueError):
        return -1


def _bg_download_ascii():
    """Descarga en segundo plano la imagen de fondo para el dialogo Universo."""
    import time as _t
    _t.sleep(5)
    _profile = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
    if not os.path.exists(_profile):
        os.makedirs(_profile)
    _dst = os.path.join(_profile, 'ascii.jpg')
    if os.path.exists(_dst):
        return
    try:
        import requests
        _url = 'https://raw.githubusercontent.com/fullstackcurso/Ruta-Fullstack/main/ascii.jpg'
        r = requests.get(_url, timeout=10)
        if r.status_code == 200 and len(r.content) > 1000:
            with open(_dst, 'wb') as f:
                f.write(r.content)
            xbmc.log("[StreamNinja] ascii.jpg downloaded OK", xbmc.LOGINFO)
    except Exception:
        pass


def start_bg_download():
    """Lanza la descarga de ascii.jpg en un hilo demonio."""
    threading.Thread(target=_bg_download_ascii, daemon=True).start()


def info_menu():
    """Submenu de informacion del addon."""
    h = _get_handle()
    li = xbmcgui.ListItem(label="[COLOR skyblue]Universo EspaKodi[/COLOR]")
    li.setArt({'icon': 'DefaultIconInfo.png'})
    xbmcplugin.addDirectoryItem(handle=h, url=_u(action="show_universo"), listitem=li, isFolder=False)

    li3 = xbmcgui.ListItem(label="Información del Addon v{0}".format(xbmcaddon.Addon().getAddonInfo('version')))
    li3.setArt({'icon': 'DefaultIconInfo.png'})
    xbmcplugin.addDirectoryItem(handle=h, url=_u(action="info"), listitem=li3, isFolder=False)

    xbmcplugin.endOfDirectory(h)


def show_universo():
    """Abre la ventana grafica Universo EspaKodi."""
    import universo
    universo.show()


def info():
    """Muestra el aviso legal e informacion del addon."""
    t = (
        "[COLOR skyblue][B]STREAMNINJA[/B][/COLOR]\n"
        "Repositorio: [COLOR lightblue]github.com/fullstackcurso[/COLOR]\n"
        "Contacto: [COLOR lightblue]t.me/rubensdfa1laberot[/COLOR]\n\n"
        "----------------------------------------------------------\n"
        "[COLOR red][B]AVISO LEGAL[/B][/COLOR]\n"
        "----------------------------------------------------------\n\n"
        "[B]1. No Afiliación:[/B]\n"
        "Este proyecto es independiente. No tiene ninguna afiliación "
        "ni vinculación con ninguna plataforma oficial.\n\n"
        "[B]2. Naturaleza Técnica:[/B]\n"
        "Este software actúa como una pasarela de red. No contiene, "
        "aloja ni sube contenido protegido. Se limita a establecer conexiones "
        "hacia las direcciones de internet elegidas libremente por el usuario.\n\n"
        "[B]3. Responsabilidad del Usuario:[/B]\n"
        "El usuario es el único responsable de verificar la legalidad "
        "del acceso a los contenidos según las leyes de su país. "
        "Este addon se proporciona \"tal cual\", sin garantías de ningún tipo. "
        "StreamNinja no se hace responsable de la información transmitida "
        "por la red local o remota a la que decidas conectarte.\n\n"
        "[B]4. Naturaleza del proyecto:[/B]\n"
        "Es GRATUITO y sin ánimo de lucro.\n\n"
        "[B]5. Telemetría Anónima:[/B]\n"
        "Para decidir qué versiones de Kodi requieren soporte prioritario, se envía de forma anónima el sistema operativo, "
        "versión del addon y de Kodi. Con esto solo se actualizan porcentajes, no se guarda ninguna información personal ni IPs. "
        "Este proyecto defiende la privacidad absoluta y no se tiene el más mínimo interés en rastrear, perfilar ni vigilar a los usuarios.\n\n"
        "[B]6. Contacto y Retirada:[/B]\n"
        "Si es titular de derechos y considera que este código viola alguna "
        "política, contacte a través de Telegram."
    )
    xbmcgui.Dialog().textviewer("Información de StreamNinja", t)
