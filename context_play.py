# -*- coding: utf-8 -*-
# StreamNinja
# Creado por RubénSDFA1laberot (github.com/fullstackcurso / github.com/espatv)
# Licencia: GPL-2.0-or-later — Consulta el archivo LICENSE para mas detalles.
"""
Menú contextual: Abrir con StreamNinja.
Extrae la ruta del item seleccionado y lanza la reproducción
a través del entry point del addon.
"""
import sys
import urllib.parse
import xbmc
import xbmcgui

if __name__ == '__main__':
    try:
        item_url = sys.listitem.getPath()
        if item_url:
            safe_url = urllib.parse.quote(item_url, safe="")
            xbmcgui.Dialog().notification(
                "StreamNinja", "Abriendo enlace...",
                xbmcgui.NOTIFICATION_INFO, 1500
            )
            xbmc.executebuiltin(
                'RunPlugin(plugin://plugin.video.streamninja/'
                '?action=url_play&url={0})'.format(safe_url)
            )
        else:
            xbmcgui.Dialog().notification(
                "StreamNinja", "No se pudo extraer la URL",
                xbmcgui.NOTIFICATION_WARNING, 2000
            )
    except Exception as e:
        xbmc.log("[StreamNinja] context_play: {0}".format(e), xbmc.LOGERROR)

