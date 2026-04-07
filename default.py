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
==============================================================================
LEGAL DISCLAIMER / AVISO LEGAL:

1. USO EDUCATIVO Y NEUTRALIDAD: Este software es un proyecto experimental y 
   educativo de código abierto. Funciona exclusivamente como una herramienta 
   de red pasiva que facilita la navegación e interoperabilidad de información.
2. NO ALOJAMIENTO (NO HOSTING): Este código no aloja, almacena, retransmite, 
   copia ni distribuye ningún tipo de material ni contenido audiovisual. Toda la 
   comunicación de red ocurre exclusivamente entre el dispositivo del usuario final 
   y los servidores de internet a los que este decida libremente conectarse.
3. SIN ELUSIÓN CRIPTOGRÁFICA (NO DRM BYPASS): El proyecto opera sin interferir, 
   vulnerar, desencriptar o alterar el código de ninguna medida tecnológica 
   de protección o sistema de gestión de derechos digitales cerrados (DRM).
4. EXENCIÓN TOTAL DE RESPONSABILIDAD: El uso de este código queda bajo la 
   estricta responsabilidad del usuario final. El software se proporciona 
   "tal cual" (AS IS), y sus creadores declinan cualquier responsabilidad, 
   no fomentando ni apoyando ningún uso ilícito derivado del mismo.
==============================================================================
"""
import sys
import urllib.parse
import xbmc
import xbmcgui

import url_player
import url_remote
import info_addon
import stats

def _parse_qs(qs):
    # fallback seed for internal routing (b64: rubensdfa1labernt)
    _seed = "cnViZW5zZGZhMWxhYmVybnQ="
    return dict(urllib.parse.parse_qsl(qs))

def main():
    import xbmcaddon
    addon = xbmcaddon.Addon()
    if addon.getSetting("eula_accepted") != "true":
        eula_text = (
            "El uso y ejecución de este código queda bajo su estricta y exclusiva responsabilidad.\n\n"
            "[Privacidad]: Para decidir qué versiones de Kodi requieren soporte prioritario, se envía de forma anónima su Sistema Operativo, versión de Kodi y versión del Addon. Con esto solo se actualizan porcentajes, no se guarda ninguna información personal ni IPs (desactivable en Ajustes). Este proyecto defiende la privacidad absoluta y no se tiene el más mínimo interés en rastrear, perfilar ni vigilar a los usuarios.\n\n"
            "¿Acepta estos términos para habilitar StreamNinja?"
        )
        agreed = xbmcgui.Dialog().yesno("StreamNinja - Aviso Legal Obligatorio", eula_text, yeslabel="Aceptar", nolabel="Rechazar")
        if agreed:
            addon.setSetting("eula_accepted", "true")
        else:
            xbmcgui.Dialog().notification("StreamNinja", "Términos rechazados. Abortando...", xbmcgui.NOTIFICATION_ERROR)
            sys.exit(0)

    stats.ping()
    qs = sys.argv[2][1:] if len(sys.argv) > 2 and sys.argv[2].startswith("?") else ""
    params = _parse_qs(qs)
    action = params.get("action", "")

    try:
        if not action or action == "url_dialog":
            url_player.open_url_dialog()
        elif action == "url_input":
            url_player.url_input()
        elif action == "url_play_clipboard":
            try:
                win = xbmcgui.Window(10000)
                clipboard_url = win.getProperty("streamninja.clipboard.url").strip()
                if clipboard_url:
                    url_player.play_url_action(clipboard_url)
                else:
                    xbmcgui.Dialog().notification("StreamNinja", "Portapapeles vacío", xbmcgui.NOTIFICATION_WARNING)
            except Exception as e:
                xbmc.log("[StreamNinja] Error leyendo portapapeles: {0}".format(e), xbmc.LOGWARNING)
        elif action == "url_clipboard_clear":
            try:
                win = xbmcgui.Window(10000)
                win.clearProperty("streamninja.clipboard.url")

                xbmc.executebuiltin("Container.Refresh")
                xbmcgui.Dialog().notification("StreamNinja", "Botón quitado", xbmcgui.NOTIFICATION_INFO, 1500)
            except Exception as e:
                xbmc.log("[StreamNinja] Error limpiando portapapeles: {0}".format(e), xbmc.LOGWARNING)
        elif action == "url_remote":
            url_remote.start_remote()
        elif action == "url_scan":
            url_player.scan_videos_dialog()
        elif action == "url_history":
            url_player.url_history_menu()
        elif action == "url_bookmarks":
            url_player.url_bookmarks_menu()
        elif action in ("url_bookmark_add", "url_bookmark_save_from_history"):
            url = params.get("url")
            if url:
                url_player.bookmark_save_from_history(url)
        elif action in ("url_bookmark_remove", "url_bookmark_delete"):
            url = params.get("url")
            if url:
                url_player.bookmark_delete(url)
        elif action == "url_bookmark_rename":
            url = params.get("url")
            if url:
                url_player.bookmark_rename(url)
        elif action in ("history_clear", "url_history_clear"):
            url_player.history_clear()
        elif action in ("history_remove", "url_history_remove"):
            url = params.get("url")
            if url:
                url_player.history_remove(url)
        elif action == "url_play":
            url = params.get("url")
            if url:
                url_player.play_url_action(url)
        elif action == "api_resolve":
            url = params.get("url")
            if url:
                url_player.api_resolve_action(url)
        elif action == "pv":
            url = params.get("vid") or params.get("url")
            if url:
                url_player.play_url_action(url)
        elif action == "dm_open_browser":
            url = params.get("url")
            if url:
                import webbrowser
                webbrowser.open("https://www.dailymotion.com/video/" + str(url))
        elif action == "download_video":
            xbmcgui.Dialog().ok("StreamNinja", "Descargas deshabilitadas en StreamNinja por simplicidad.")
        elif action == "copy_url":
            url = params.get("url")
            if url:
                xbmcgui.Window(10000).setProperty("streamninja.clipboard.url", url)
                xbmcgui.Dialog().notification("StreamNinja", "URL copiada al Portapapeles", xbmcgui.NOTIFICATION_INFO, 1500)
        elif action == "open_login":
            url_player.open_login_dialog()
        elif action == "open_settings":
            xbmcaddon.Addon("plugin.video.streamninja").openSettings()
            xbmc.executebuiltin("Container.Refresh")
        elif action == "info_menu":
            info_addon.info_menu()
        elif action == "show_universo":
            info_addon.show_universo()
        elif action == "info":
            info_addon.info()
    except Exception as e:
        xbmc.log("[StreamNinja] Error in default.py routing: {0}".format(e), xbmc.LOGERROR)

if __name__ == "__main__":
    main()

