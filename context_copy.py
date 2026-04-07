# -*- coding: utf-8 -*-
# StreamNinja
# Creado por RubénSDFA1laberot (github.com/fullstackcurso / github.com/espatv)
# Licencia: GPL-2.0-or-later — Consulta el archivo LICENSE para mas detalles.
"""
Menú contextual: Copiar a StreamNinja.
Guarda la ruta del item seleccionado en la propiedad global
del addon para poder pegarla y reproducirla después.
"""
import sys
import xbmc
import xbmcgui

if __name__ == '__main__':
    try:
        item_url = sys.listitem.getPath()
        if item_url:
            xbmcgui.Window(10000).setProperty(
                "streamninja.clipboard.url", item_url
            )
            xbmcgui.Dialog().notification(
                "StreamNinja", "URL copiada en memoria",
                xbmcgui.NOTIFICATION_INFO, 2000
            )
        else:
            xbmcgui.Dialog().notification(
                "StreamNinja", "No se pudo extraer la URL del vídeo",
                xbmcgui.NOTIFICATION_WARNING, 2000
            )
    except Exception as e:
        xbmc.log("[StreamNinja] context_copy: {0}".format(e), xbmc.LOGERROR)

