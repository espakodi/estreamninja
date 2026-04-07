# -*- coding: utf-8 -*-
# StreamNinja — Copyright (C) 2024-2026 RubénSDFA1laberot (github.com/fullstackcurso)
# Licencia: GPL-2.0-or-later — Consulta el archivo LICENSE para mas detalles.
#
# ESTREAMNINJA EXPERIMENTAL:
# EstreamNinja es una versión experimental donde se prueban funcionalidades que puede que lleguen a StreamNinja o no.
# Y además tiene la peculiaridad de que está todo en español, que es el idioma nativo de RubénSDFA1laberot,
# para facilitar el desarrollo. Esta versión no está pensada para ser usada por usuarios finales ni por desarrolladores,
# ya que ni siquiera se ha comentado el código como es debido. Y hay mucho código que no se usa ni está pulido.
"""
Universo EspaKodi
====================
Ventana informativa con enlaces a los proyectos relacionados,
canales de Telegram y contacto.
"""
import os
import xbmc
import xbmcgui
import xbmcaddon
import xbmcvfs

_ADDON_PATH = xbmcaddon.Addon().getAddonInfo("path")
_MEDIA = os.path.join(_ADDON_PATH, "resources", "media")
_TEX = os.path.join(_MEDIA, "white.png")
_TRANSP = os.path.join(_MEDIA, "transparent.png")
_FOCUS = os.path.join(_MEDIA, "focus.png")

W, H = 1280, 720
PW, PH = 520, 480
PX, PY = (W - PW) // 2, (H - PH) // 2




class UniversoDialog(xbmcgui.WindowDialog):
    """Diálogo con enlaces al ecosistema StreamNinja."""

    def __init__(self):
        super().__init__()
        self.url_map = {}
        self.all_buttons = []
        self.close_btn_id = -1
        self.reveal_btn_id = -1
        self.bg_img = None
        self.all_controls = []
        self._build()

    def _mk_img(self, x, y, w, h, color, img=None):
        c = xbmcgui.ControlImage(x, y, w, h, img or _TEX, colorDiffuse=color)
        self._pending.append(c)
        self.all_controls.append(c)
        return c

    def _mk_lbl(self, x, y, w, h, text, font="font13", color="FFFFFFFF", align=0):
        c = xbmcgui.ControlLabel(
            x, y, w, h, text, font=font, textColor=color, alignment=align
        )
        self._pending.append(c)
        self.all_controls.append(c)
        return c

    def _mk_btn(self, x, y, w, h, text, tc="FFFFFFFF", fc="FFFFFFFF", align=0x04):
        c = xbmcgui.ControlButton(
            x, y, w, h, text,
            font="font12", textColor=tc, focusedColor=fc, alignment=align,
            noFocusTexture=_TRANSP, focusTexture=_FOCUS,
        )
        self._pending.append(c)
        self.all_controls.append(c)
        return c

    def _build(self):
        self._pending = []

        # Panel central semi-transparente
        self._mk_img(PX, PY, PW, PH, "D0111922")

        # Imagen secreta precargada pero oculta
        _profile = xbmcvfs.translatePath(xbmcaddon.Addon().getAddonInfo('profile'))
        bg_path = os.path.join(_profile, 'ascii.jpg')
        if os.path.exists(bg_path):
            self.bg_img = xbmcgui.ControlImage(PX, PY, PW, PH, bg_path, colorDiffuse='FFFFFFFF')
            self._pending.append(self.bg_img)

        # Línea superior decorativa
        self._mk_img(PX, PY, PW, 3, "FF3090FF")

        # Título con botón reveal
        y = PY + 17
        reveal = xbmcgui.ControlButton(PX, y, PW, 25,
                          '[B]*  Universo EspaKodi  >[/B]',
                          font='font13', textColor='FF3090FF', focusedColor='FFFFFFFF', alignment=0x02,
                          noFocusTexture=_TRANSP, focusTexture=_FOCUS)
        self._pending.append(reveal)
        self.all_controls.append(reveal)
        self.all_buttons.append(reveal)
        y += 40
        self._mk_img(PX + 35, y, PW - 70, 1, "30FFFFFF")
        y += 15

        # Enlaces
        links = [
            ("FFFFD700", "Contacto", "https://t.me/rubensdfa1laberot/?direct"),
            (None, None, None),
            ("FF3090FF", "EspaTV (principal)", "https://github.com/espatv"),
            ("FF3090FF", "FullStackCurso", "https://github.com/fullstackcurso"),
            ("FF3090FF", "EspaKodi", "https://github.com/espakodi"),
            ("FF3090FF", "LoioLoio (multi)", "https://github.com/loioloio"),
            (None, None, None),
            ("FF2AABEE", "Canal de Telegram", "https://t.me/espadaily"),
            ("FF2AABEE", "Chat EspaKodi", "https://t.me/espakodi"),
        ]

        self._link_buttons = []  # Para asignar URLs después del batch
        for color, label, url in links:
            if color is None:
                y += 6
                self._mk_img(PX + 35, y, PW - 70, 1, "30FFFFFF")
                y += 10
                continue
            
            self._mk_lbl(
                PX + 50, y, PW - 100, 24,
                "[B]{0}[/B]".format(label),
                font="font13", color=color, align=0x04
            )
            btn = xbmcgui.ControlButton(
                PX + 35, y, PW - 70, 24,
                "[B]" + url.replace("https://", "") + "[/B]  ",
                font="font13", textColor="FFCCCCCC", focusedColor="FFFFFFFF",
                alignment=0x01 | 0x04,
                noFocusTexture=_TRANSP, focusTexture=_FOCUS,
            )
            self._pending.append(btn)
            self.all_controls.append(btn)
            self._link_buttons.append((btn, url))
            self.all_buttons.append(btn)
            y += 28

        # Separador final
        self._mk_img(PX + 35, y, PW - 70, 1, "30FFFFFF")
        y += 15

        # Botón cerrar
        close = self._mk_btn(
            PX + (PW - 180) // 2, y, 180, 32,
            "[B]Cerrar[/B]", tc="FF888888", align=0x02 | 0x04,
        )
        self.all_buttons.append(close)

        # === BATCH: una sola llamada IPC en vez de ~25 ===
        self.addControls(self._pending)

        # Asignar IDs después del batch (solo disponibles tras addControls)
        self.reveal_btn_id = reveal.getId()
        self.close_btn_id = close.getId()
        for btn, url in self._link_buttons:
            self.url_map[btn.getId()] = url

        if self.bg_img:
            self.bg_img.setVisible(False)

        # Navegación circular entre botones
        for i in range(len(self.all_buttons)):
            b = self.all_buttons[i]
            if i > 0:
                b.controlUp(self.all_buttons[i - 1])
            if i < len(self.all_buttons) - 1:
                b.controlDown(self.all_buttons[i + 1])
        self.all_buttons[0].controlUp(self.all_buttons[-1])
        self.all_buttons[-1].controlDown(self.all_buttons[0])
        self.setFocus(self.all_buttons[0])

    def _handle_click(self, control_id):
        if control_id == self.close_btn_id:
            self.close()
            return
        if control_id == self.reveal_btn_id:
            if self.bg_img:
                for c in self.all_controls:
                    c.setVisible(False)
                self.bg_img.setVisible(True)
                xbmcgui.Dialog().notification("Universo EspaKodi", "Fundado por RubenSDFA1laberot", xbmcgui.NOTIFICATION_INFO, 3000)
                import time as _t
                _t.sleep(3)
                self.bg_img.setVisible(False)
                for c in self.all_controls:
                    c.setVisible(True)
                self.bg_img.setVisible(False)
            return
        url = self.url_map.get(control_id)
        if url:
            try:
                if xbmc.getCondVisibility("System.Platform.Android"):
                    xbmc.executebuiltin(
                        'StartAndroidActivity("","android.intent.action.VIEW","","{0}")'.format(url)
                    )
                else:
                    import webbrowser
                    webbrowser.open(url)
                xbmcgui.Dialog().notification(
                    "StreamNinja", "Abriendo...",
                    xbmcgui.NOTIFICATION_INFO, 2000,
                )
            except Exception:
                xbmcgui.Dialog().ok(
                    "Enlace StreamNinja",
                    "Abre esta URL:\n\n" + url,
                )

    def onAction(self, action):
        aid = action.getId()
        if aid in (10, 92, 110):
            self.close()
        elif aid in (7, 100, 101):
            self._handle_click(self.getFocusId())

    def onClick(self, controlId):
        self._handle_click(controlId)


def show():
    """Muestra el diálogo Universo EspaKodi."""
    bg = None
    try:
        import ascii_matrix
        bg = ascii_matrix.get_bg_dialog()
        if bg:
            bg.show()
    except Exception:
        pass

    dlg = UniversoDialog()
    dlg.doModal()

    if bg:
        try:
            bg.close()
        except Exception:
            pass
    del dlg