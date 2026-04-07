# -*- coding: utf-8 -*-
#
# ESTREAMNINJA EXPERIMENTAL:
# EstreamNinja es una versión experimental donde se prueban funcionalidades que puede que lleguen a StreamNinja o no.
# Y además tiene la peculiaridad de que está todo en español, que es el idioma nativo de RubénSDFA1laberot,
# para facilitar el desarrollo. Esta versión no está pensada para ser usada por usuarios finales ni por desarrolladores,
# ya que ni siquiera se ha comentado el código como es debido. Y hay mucho código que no se usa ni está pulido.
"""
Campo estelar animado via skin XML.
Genera labels individuales en un grupo con animaciones slide/fade.
"""
import os
import random
import xbmcgui
import xbmcaddon

_ID = xbmcaddon.Addon().getAddonInfo("id")
_ADDON_PATH = xbmcaddon.Addon().getAddonInfo("path")
_MEDIA_URI = "special://home/addons/{}/resources/media/".format(_ID)

_SKIN_BASE = os.path.join(_ADDON_PATH, "resources", "skins", "Default", "1080i")
XML_NAME = "script-stars-v5.xml"
XML_PATH = os.path.join(_SKIN_BASE, XML_NAME)

_ROWS = [
    " .       *             +          .   x          .          *    .         +       ",
    "       +        .            .              *           +            x             ",
    "  x              +      .       .             +               .        x   *       ",
    "      .      *               +          x            *         .            +      ",
    "  .               +                   .          *             +       .           ",
    "       x       .           *               .         .           +        *        ",
    " .                   +               x           .          *           +          ",
    "         +                 .                .          +              *       .     "
]


def _build_xml():
    """Genera el XML del campo estelar."""
    rng = random.Random()
    
    label_controls = []
    y = 0
    line_height = 42
    
    for _pass in range(2):
        for i in range(25):
            row = "    ".join(rng.choice(_ROWS) for _ in range(5))
            row = row.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            label_controls.append(
                '            <control type="label">\n'
                '                <left>0</left>\n'
                '                <top>{y}</top>\n'
                '                <width>3000</width>\n'
                '                <height>{h}</height>\n'
                '                <font>font12</font>\n'
                '                <textcolor>AABBFFFF</textcolor>\n'
                '                <label>{text}</label>\n'
                '            </control>'.format(y=y, h=line_height, text=row)
            )
            y += line_height

    labels_xml = "\n".join(label_controls)
    half_h = (25 * line_height)

    xml = """<?xml version="1.0" encoding="utf-8"?>
<window>
    <defaultcontrol>2</defaultcontrol>
    <controls>
        <control type="image">
            <left>0</left>
            <top>0</top>
            <width>1920</width>
            <height>1080</height>
            <texture>{media}white.png</texture>
            <colordiffuse>F2030610</colordiffuse>
        </control>

        <control type="group">
            <left>0</left>
            <top>-{half_h}</top>
            <width>1920</width>

            <!-- Palpitacion -->
            <animation effect="fade" start="35" end="100" time="2000" pulse="true" condition="true">Conditional</animation>
            
            <!-- Caida vertical lenta -->
            <animation effect="slide" start="0,0" end="0,{half_h}" time="45000" loop="true" condition="true">Conditional</animation>
            
{labels}
        </control>

        <control type="button" id="2">
            <left>0</left>
            <top>1200</top>
            <width>1</width>
            <height>1</height>
            <label> </label>
            <visible>false</visible>
        </control>
    </controls>
</window>
""".format(
        media=_MEDIA_URI,
        labels=labels_xml,
        half_h=half_h
    )
    return xml


class AsciiMatrixXML(xbmcgui.WindowXMLDialog):
    def __init__(self, *args, **kwargs):
        super(AsciiMatrixXML, self).__init__(*args, **kwargs)

    def onInit(self):
        pass

    def onAction(self, action):
        if action.getId() in (9, 10, 92, 216):
            self.close()


def _ensure_xml():
    """Genera el XML solo la primera vez."""
    if not os.path.exists(_SKIN_BASE):
        os.makedirs(_SKIN_BASE)
    if not os.path.exists(XML_PATH):
        xml = _build_xml()
        with open(XML_PATH, "w", encoding="utf-8") as f:
            f.write(xml)


def show():
    """Abre la lluvia de estrellas a pantalla completa."""
    _ensure_xml()
    dlg = AsciiMatrixXML(XML_NAME, _ADDON_PATH, "Default", "1080i")
    dlg.doModal()
    del dlg


def get_bg_dialog():
    """Devuelve la escena estelar para usarla de fondo cosmico."""
    _ensure_xml()
    dlg = AsciiMatrixXML(XML_NAME, _ADDON_PATH, "Default", "1080i")
    return dlg
