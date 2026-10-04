# -*- coding: utf-8 -*-
"""HackHet - Gestion des participants (admin dashboard).
Run with:  python hackhet_dashboard.py
Requires:  Python 3.10+ and PySide6 (pip install PySide6).
"""
import os
import sys
import tempfile

from PySide6.QtCore import QByteArray, QEasingCurve, Qt, QRect, QRectF, QSize
from PySide6.QtGui import (QColor, QFont, QFontMetrics, QIcon, QImage, QLinearGradient,
                           QPainter, QPainterPath, QPen, QPixmap)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QFrame, QGraphicsDropShadowEffect,
                               QHBoxLayout, QLabel, QLineEdit, QMainWindow, QPushButton,
                               QScrollArea, QSizePolicy, QVBoxLayout, QWidget)

# ----------------------------------------------------------------------------
# Design tokens
# ----------------------------------------------------------------------------
PAGE_BG = "#f4f6fd"
CARD_BORDER = "#eef0fb"
INK = "#141a3d"
BODY = "#5b6384"
MUTED = "#8b92ae"
LINES = "#e6e9f6"
PRIMARY = "#3f46f0"
GRAD_A = "#3a45ef"
GRAD_B = "#5d4ef7"
GREEN = "#1fb67a"
GREEN_D = "#2fae6b"
PINK = "#f0457f"
BLUE = "#2b8cf0"
ORANGE = "#f5a623"
VIOLET = "#7b3fe4"
DANGER = "#e5384f"
FONT_STACK = "'Inter', 'Plus Jakarta Sans', 'Segoe UI', 'Helvetica Neue', Arial"

# ----------------------------------------------------------------------------
# Inline SVG icons (Feather-style, 24x24, stroke only, round caps/joins)
# ----------------------------------------------------------------------------
ICONS = {
    "home": '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>'
             '<polyline points="9 22 9 12 15 12 15 22"/>',
    "user": '<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>'
              '<circle cx="12" cy="7" r="4"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
               '<circle cx="9" cy="7" r="4"/>'
               '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
               '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>',
    "briefcase": '<rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>'
                   '<path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>',
    "star": '<polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 '
              '12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>',
    "calendar": '<rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>'
                  '<line x1="16" y1="2" x2="16" y2="6"/>'
                  '<line x1="8" y1="2" x2="8" y2="6"/>'
                  '<line x1="3" y1="10" x2="21" y2="10"/>',
    "settings": '<circle cx="12" cy="12" r="3"/>'
                  '<path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 '
                  '2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 '
                  '1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 '
                  '1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 '
                  '1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 '
                  '1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 '
                  '2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 '
                  '2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 '
                  '1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 '
                  '0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 '
                  '1.65 0 0 0-1.51 1z"/>',
    "search": '<circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>',
    "bell": '<path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>'
              '<path d="M13.73 21a2 2 0 0 1-3.46 0"/>',
    "mail": '<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>'
              '<polyline points="22,6 12,13 2,6"/>',
    "chevron-down": '<polyline points="6 9 12 15 18 9"/>',
    "chevron-up": '<polyline points="18 15 12 9 6 15"/>',
    "chevron-left": '<polyline points="15 18 9 12 15 6"/>',
    "chevron-right": '<polyline points="9 18 15 12 9 6"/>',
    "arrow-right": '<line x1="5" y1="12" x2="19" y2="12"/>'
                     '<polyline points="12 5 19 12 12 19"/>',
    "plus": '<line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>',
    "sliders": '<line x1="4" y1="21" x2="4" y2="14"/><line x1="4" y1="10" x2="4" y2="3"/>'
                 '<line x1="12" y1="21" x2="12" y2="12"/><line x1="12" y1="8" x2="12" y2="3"/>'
                 '<line x1="20" y1="21" x2="20" y2="16"/><line x1="20" y1="12" x2="20" y2="3"/>'
                 '<line x1="1" y1="14" x2="7" y2="14"/><line x1="9" y1="8" x2="15" y2="8"/>'
                 '<line x1="17" y1="16" x2="23" y2="16"/>',
    "filter": '<polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>',
    "eye": '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>'
             '<circle cx="12" cy="12" r="3"/>',
    "edit": '<path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>',
    "trash": '<polyline points="3 6 5 6 21 6"/>'
               '<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "pie": '<path d="M21.21 15.89A10 10 0 1 1 8 2.83"/>'
             '<path d="M22 12A10 10 0 0 0 12 2v10z"/>',
    "cpu": '<rect x="4" y="4" width="16" height="16" rx="2" ry="2"/>'
             '<rect x="9" y="9" width="6" height="6"/>'
             '<line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/>'
             '<line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/>'
             '<line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/>'
             '<line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
    "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    "globe": '<circle cx="12" cy="12" r="10"/>'
               '<line x1="2" y1="12" x2="22" y2="12"/>'
               '<path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 '
               '15.3 15.3 0 0 1 4-10z"/>',
    "pen": '<path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/>',
    "share": '<circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/>'
               '<circle cx="18" cy="19" r="3"/>'
               '<line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/>'
               '<line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>',
    "trophy": '<path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"/>'
                '<path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"/>'
                '<path d="M4 22h16"/><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"/>'
                '<path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"/>'
                '<path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"/>',
    "bulb": '<path d="M9 18h6"/><path d="M10 22h4"/>'
              '<path d="M12 2a7 7 0 0 0-4.6 12.3c.7.6 1.1 1.4 1.1 2.2V17h7v-.5c0-.8.4-1.6 '
              '1.1-2.2A7 7 0 0 0 12 2z"/>',
    "leaf": '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 .5 4.5-1 6.5C15 12 11 20 11 20z"/>'
              '<path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/>',
    "gamepad": '<line x1="6" y1="12" x2="10" y2="12"/><line x1="8" y1="10" x2="8" y2="14"/>'
                 '<line x1="15" y1="13" x2="15.01" y2="13"/><line x1="18" y1="11" x2="18.01" y2="11"/>'
                 '<path d="M17.32 5H6.68a4 4 0 0 0-3.98 3.59c-.02.21-.7 6.83-.7 6.91a2.5 2.5 0 0 0 '
                 '2.49 2.5h13.02a2.5 2.5 0 0 0 2.49-2.5c0-.08-.68-6.7-.7-6.91A4 4 0 0 0 17.32 5z"/>',
    "check": '<polyline points="20 6 9 17 4 12"/>',
}

_pixmap_cache = {}
_chevron_url = None


def svg_pixmap(name, color, size, stroke=2.0):
    """Render an inline feather-style SVG icon to a crisp QPixmap."""
    key = (name, color, int(size), float(stroke))
    pm = _pixmap_cache.get(key)
    if pm is not None and not pm.isNull():
        return pm
    body = ICONS.get(name, ICONS["search"])
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" '
        'viewBox="0 0 24 24" fill="none" stroke="%s" stroke-width="%s" '
        'stroke-linecap="round" stroke-linejoin="round">%s</svg>'
        % (color, stroke, body)
    )
    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    dpr = 2.0
    try:
        app = QApplication.instance()
        if app is not None:
            scr = app.primaryScreen()
            if scr is not None:
                dpr = float(scr.devicePixelRatio()) or 2.0
    except Exception:
        dpr = 2.0
    px = max(1, int(size * dpr))
    pix = QPixmap(px, px)
    pix.setDevicePixelRatio(dpr)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing, True)
    renderer.render(painter, QRectF(0, 0, size, size))
    painter.end()
    _pixmap_cache[key] = pix
    return pix


def get_chevron_url():
    """Render the combo chevron to a temp PNG and return its file url."""
    global _chevron_url
    if _chevron_url:
        return _chevron_url
    pm = svg_pixmap("chevron-down", "#8b92ae", 12, 2.2)
    img = pm.toImage()
    path = os.path.join(tempfile.gettempdir(), "hackhet_chevron.png")
    try:
        img.save(path, "PNG")
    except Exception:
        pass
    _chevron_url = path.replace(chr(92), "/")
    return _chevron_url


def card_shadow(widget, blur=30, dy=6, alpha=0.11):
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    eff.setOffset(0, dy)
    eff.setColor(QColor(60, 70, 170, int(alpha * 255)))
    widget.setGraphicsEffect(eff)
    return eff


def glow_shadow(widget, color="#3c46f0", blur=24, dy=6, alpha=0.35):
    c = QColor(color)
    r, g, b = c.red(), c.green(), c.blue()
    eff = QGraphicsDropShadowEffect(widget)
    eff.setBlurRadius(blur)
    eff.setOffset(0, dy)
    eff.setColor(QColor(r, g, b, int(alpha * 255)))
    widget.setGraphicsEffect(eff)
    return eff


def icon_label(name, color, size, stroke=2.0):
    lab = QLabel()
    lab.setPixmap(svg_pixmap(name, color, size, stroke))
    lab.setFixedSize(QSize(int(size), int(size)))
    lab.setAlignment(Qt.AlignCenter)
    lab.setAttribute(Qt.WA_TransparentForMouseEvents, True)
    return lab

# ----------------------------------------------------------------------------
# Custom painted widgets
# ----------------------------------------------------------------------------
class LogoMark(QWidget):
    """66x70 hexagonal cube mark with a white rounded H on top."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(66, 70)
        self.setAttribute(Qt.WA_TransparentForMouseEvents, True)

    def sizeHint(self):
        return QSize(66, 70)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        cx, cy = 33.0, 36.0
        r = 26.0
        import math
        pts_top, pts_left, pts_right = [], [], []
        for i in range(6):
            ang = math.radians(60 * i - 90)
            x = cx + r * math.cos(ang)
            y = cy + r * math.sin(ang)
            (pts_top if i < 2 else pts_left if i < 4 else pts_right).append((x, y))
        top = [(cx, cy)] + pts_top + [(cx + r * math.cos(math.radians(150)), cy + r * math.sin(math.radians(150)))]
        g1 = QLinearGradient(cx, cy - r, cx, cy)
        g1.setColorAt(0, QColor("#8b5cf6"))
        g1.setColorAt(1, QColor("#6d4cf5"))
        path = QPainterPath()
        path.moveTo(cx, cy)
        path.lineTo(cx + r * 0.95, cy - r * 0.55)
        path.lineTo(cx, cy - r)
        path.lineTo(cx - r * 0.95, cy - r * 0.55)
        path.closeSubpath()
        p.fillPath(path, g1)
        g2 = QLinearGradient(cx, cy, cx + r, cy + r)
        g2.setColorAt(0, QColor("#4338ca"))
        g2.setColorAt(1, QColor("#3b44f0"))
        path2 = QPainterPath()
        path2.moveTo(cx, cy)
        path2.lineTo(cx + r * 0.95, cy - r * 0.55)
        path2.lineTo(cx + r * 0.95, cy + r * 0.55)
        path2.lineTo(cx, cy + r)
        path2.closeSubpath()
        p.fillPath(path2, g2)
        g3 = QLinearGradient(cx - r, cy, cx, cy + r)
        g3.setColorAt(0, QColor("#2f7bf0"))
        g3.setColorAt(1, QColor("#1fb2ff"))
        path3 = QPainterPath()
        path3.moveTo(cx, cy)
        path3.lineTo(cx - r * 0.95, cy - r * 0.55)
        path3.lineTo(cx - r * 0.95, cy + r * 0.55)
        path3.lineTo(cx, cy + r)
        path3.closeSubpath()
        p.fillPath(path3, g3)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#ffffff"))
        p.drawRoundedRect(QRect(22, 22, 7, 28), 3, 3)
        p.drawRoundedRect(QRect(37, 22, 7, 28), 3, 3)
        p.drawRoundedRect(QRect(22, 32, 22, 7), 3, 3)


class DonutWidget(QWidget):
    def __init__(self, segments, parent=None):
        super().__init__(parent)
        self.segments = segments  # list of (value, color)
        self.setFixedSize(132, 132)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        rect = QRectF(8, 8, 116, 116)
        pen = QPen(QColor("#e9ecf8"))
        pen.setWidth(15)
        pen.setCapStyle(Qt.FlatCap)
        p.setPen(pen)
        p.drawEllipse(rect)
        total = float(sum(v for v, _ in self.segments)) or 1.0
        gap = 3.0
        angle = 90.0
        for value, color in self.segments:
            span = 360.0 * value / total
            pen2 = QPen(QColor(color))
            pen2.setWidth(15)
            pen2.setCapStyle(Qt.FlatCap)
            p.setPen(pen2)
            p.drawArc(rect, int((angle - span + gap / 2) * 16), int((span - gap) * 16))
            angle -= span
        p.setPen(QColor(INK))
        f = QFont("Inter, Segoe UI, Arial", 26, QFont.Bold)
        p.setFont(f)
        p.drawText(QRect(0, 44, 132, 34), Qt.AlignHCenter | Qt.AlignVCenter, "120")
        p.setPen(QColor(BODY))
        f2 = QFont("Inter, Segoe UI, Arial", 9)
        p.setFont(f2)
        p.drawText(QRect(0, 72, 132, 18), Qt.AlignHCenter | Qt.AlignVCenter, "participants")


class ProgressWidget(QWidget):
    def __init__(self, value, max_value=51, grad=("#4f46e5", "#6d5ff7"), parent=None):
        super().__init__(parent)
        self.value = value
        self.max_value = max_value
        self.grad = grad
        self.setFixedHeight(5)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        w, h = float(self.width()), 5.0
        y = (self.height() - h) / 2.0
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#eef0fa"))
        p.drawRoundedRect(QRectF(0, y, w, h), h / 2, h / 2)
        frac = max(0.0, min(1.0, self.value / float(self.max_value)))
        bw = max(h, w * frac)
        g = QLinearGradient(0, 0, w, 0)
        g.setColorAt(0, QColor(self.grad[0]))
        g.setColorAt(1, QColor(self.grad[1]))
        p.setBrush(g)
        p.drawRoundedRect(QRectF(0, y, bw, h), h / 2, h / 2)


class AvatarWidget(QWidget):
    """42px circle avatar: light-blue bg + navy hair, skin face, indigo shoulders."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(42, 42)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor("#dbe3ff"))
        p.drawEllipse(0, 0, 42, 42)
        p.save()
        path = QPainterPath()
        path.addEllipse(0, 0, 42, 42)
        p.setClipPath(path)
        p.setBrush(QColor("#3b46c4"))
        p.drawEllipse(QRect(4, 30, 34, 20))
        p.setBrush(QColor("#f2c9a4"))
        p.drawEllipse(QRect(12, 10, 18, 19))
        p.setBrush(QColor("#232a55"))
        p.drawRoundedRect(QRect(11, 6, 20, 12), 6, 6)
        p.setBrush(QColor("#f2c9a4"))
        p.drawEllipse(QRect(12, 15, 18, 14))
        p.setBrush(QColor("#232a55"))
        p.drawRoundedRect(QRect(12, 8, 18, 8), 4, 4)
        p.restore()


class NotifButton(QPushButton):
    """Circular 42px white button with icon + red dot (white 2px ring)."""
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self.icon_name = icon
        self.setFixedSize(42, 42)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            "QPushButton { background: #ffffff; border: 1px solid #eceffa; border-radius: 21px; }"
            "QPushButton:hover { background: #f2f4ff; }"
        )
        card_shadow(self, blur=18, dy=4, alpha=0.10)
        lay = QHBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setAlignment(Qt.AlignCenter)
        lab = icon_label(icon, PRIMARY, 20, 1.9)
        lay.addWidget(lab)

    def paintEvent(self, event):
        super().paintEvent(event)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(QPen(QColor("#ffffff"), 2))
        p.setBrush(QColor("#ef4444"))
        p.drawEllipse(QRect(28, 5, 9, 9))


class AvatarBadge(QLabel):
    """36px circular avatar with 2-letter initials (pastel bg + darker text)."""
    def __init__(self, initials, bg, fg, parent=None):
        super().__init__(parent)
        self.initials = initials
        self.bg = bg
        self.fg = fg
        self.setFixedSize(36, 36)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        p.setPen(Qt.NoPen)
        p.setBrush(QColor(self.bg))
        p.drawEllipse(0, 0, 36, 36)
        p.setPen(QColor(self.fg))
        f = QFont("Inter, Segoe UI, Arial", 13, QFont.Bold)
        p.setFont(f)
        p.drawText(self.rect(), Qt.AlignCenter, self.initials)


class BadgeDot(QLabel):
    def __init__(self, diameter, grad, icon, icon_color="#ffffff", icon_size=22, parent=None):
        super().__init__(parent)
        self.diameter = int(diameter)
        self.grad = grad
        self.icon = icon
        self.icon_color = icon_color
        self.icon_size = int(icon_size)
        self.setFixedSize(self.diameter, self.diameter)
        if icon:
            pm = svg_pixmap(icon, icon_color, self.icon_size, 2.0)
            self.setPixmap(pm)
            self.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        d = float(self.diameter)
        if isinstance(self.grad, (list, tuple)):
            g = QLinearGradient(0, 0, d, d)
            g.setColorAt(0, QColor(self.grad[0]))
            g.setColorAt(1, QColor(self.grad[1]))
            p.setBrush(g)
        else:
            p.setBrush(QColor(self.grad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QRectF(0, 0, d, d))
        if self.icon:
            pm = svg_pixmap(self.icon, self.icon_color, self.icon_size, 2.0)
            x = (d - self.icon_size) / 2.0
            y = (d - self.icon_size) / 2.0
            p.drawPixmap(QRectF(x, y, self.icon_size, self.icon_size), pm, QRectF(pm.rect()))

# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
PARTICIPANTS = [
    dict(initials="SB", name="Sarah Ben Ali", school="ESPRIT", email="sarah.benali@esprit.tn", role="Etudiant", team="GreenTech", status="Actif", bg="#e8dcff", fg="#7a45e0"),
    dict(initials="MT", name="Mohamed Trabelsi", school="ESPRIT", email="mohamed.trabelsi@esprit.tn", role="Etudiant", team="CodeCraft", status="Actif", bg="#d9e6ff", fg="#2b5fd9"),
    dict(initials="LK", name="Lina Karkni", school="ESPRIT", email="lina.karkni@esprit.tn", role="Etudiant", team="PixelForce", status="Actif", bg="#ffdfe4", fg="#e0445f"),
    dict(initials="OJ", name="Omar Jelassi", school="ISET", email="omar.jelassi@iset.tn", role="Etudiant", team="GreenTech", status="Actif", bg="#d9f5e6", fg="#1f9d62"),
    dict(initials="NC", name="Nour Chatti", school="ESPRIT", email="nour.chatti@esprit.tn", role="Etudiant", team="CodeCraft", status="Actif", bg="#dfe3ff", fg="#4b4fe0"),
    dict(initials="YM", name="Yassine Mhiri", school="ISET", email="yassine.mhiri@iset.tn", role="Enseignant", team="", status="Actif", bg="#ead9ff", fg="#8a3fe0"),
    dict(initials="MS", name="Maya Sassi", school="ESPRIT", email="maya.sassi@esprit.tn", role="Etudiant", team="PixelForce", status="Actif", bg="#d8f0ff", fg="#1f8ad0"),
    dict(initials="KF", name="Karim Fekih", school="ISET", email="karim.fekih@iset.tn", role="Professionnel", team="", status="Actif", bg="#ffe3d0", fg="#e0642b"),
    dict(initials="RG", name="Rania Gharbi", school="ESPRIT", email="rania.gharbi@esprit.tn", role="Etudiant", team="GreenTech", status="Actif", bg="#d9f5e6", fg="#1f9d62"),
    dict(initials="TB", name="Tarek Bouzid", school="ISET", email="tarek.bouzid@iset.tn", role="Autre", team="", status="Inactif", bg="#e6e8ff", fg="#4a46c0"),
]
ROLE_DISPLAY = {"Etudiant": "Etudiant", "Enseignant": "Enseignant", "Professionnel": "Professionnel", "Autre": "Autre"}
ROLE_STYLE = {
    "Etudiant": ("#e3e5ff", "#4a46d8"),
    "Enseignant": ("#e8dcff", "#7b3fe4"),
    "Professionnel": ("#ffecbd", "#e49b0f"),
    "Autre": ("#e9ebf3", "#6b7391"),
}
STATUS_STYLE = {"Actif": ("#dcf5e7", "#2fae6b"), "Inactif": ("#ffe0e3", "#e5384f")}
COL_STRETCH = [35, 165, 170, 100, 112, 108, 126]

NAV_ITEMS = [
    ("Accueil", "home"), ("Participants", "user"), ("Organisateurs", "users"),
    ("Sponsors", "briefcase"), ("Equipes", "users"), ("Jury", "star"),
    ("Evenements", "calendar"), ("Parametres", "settings"),
]
NAV_LABELS = {"Accueil": "Accueil", "Participants": "Participants", "Organisateurs": "Organisateurs", "Sponsors": "Sponsors", "Equipes": "Equipes", "Jury": "Jury", "Evenements": "Evenements", "Parametres": "Parametres"}

NAV_LABELS = {"Accueil": "Accueil", "Participants": "Participants", "Organisateurs": "Organisateurs", "Sponsors": "Sponsors", "Equipes": "\u00c9quipes", "Jury": "Jury", "Evenements": "\u00c9v\u00e9nements", "Parametres": "Param\u00e8tres"}
ROLE_DISPLAY = {"Etudiant": "\u00c9tudiant", "Enseignant": "Enseignant", "Professionnel": "Professionnel", "Autre": "Autre"}


def norm(s):
    return (s or "").replace("\u00c9", "E").replace("\u00e9", "e").replace("\u00e8", "e").replace("\u00ea", "e").lower()


def style_card(w):
    w.setStyleSheet("QFrame { background: #ffffff; border: 1px solid %s; border-radius: 14px; }" % CARD_BORDER)
    card_shadow(w)
    return w


_uid = [0]

def transparent_widget(w):
    _uid[0] += 1
    name = "tw%d" % _uid[0]
    w.setObjectName(name)
    w.setStyleSheet("QWidget#%s { background: transparent; border: none; }" % name)
    return w


def clickable(w):
    w.setCursor(Qt.PointingHandCursor)
    return w


def pill(text, bg, fg):
    lab = QLabel(text)
    lab.setAlignment(Qt.AlignCenter)
    lab.setStyleSheet(
        "QLabel { background: %s; color: %s; font-size: 10px; font-weight: 600; "
        "border-radius: 11px; padding: 0px 12px; }" % (bg, fg)
    )
    lab.setFixedHeight(22)
    return lab


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(272)
        self.active = "Participants"
        self.buttons = {}
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 16, 15, 10)
        root.setSpacing(0)
        logo_row = QHBoxLayout()
        logo_row.setSpacing(12)
        logo_row.setContentsMargins(6, 0, 0, 0)
        logo_row.addWidget(LogoMark())
        txt = QVBoxLayout()
        txt.setSpacing(2)
        txt.setContentsMargins(0, 12, 0, 0)
        title = QLabel("HackHet")
        title.setStyleSheet(
            "QLabel { color: #ffffff; background: transparent; border: none; font-size: 31px; font-weight: 800; font-family: %s; }" % FONT_STACK
        )
        sub = QLabel("SMART HACKATHON MANAGEMENT")
        sub.setStyleSheet(
            "QLabel { color: #d4d8f7; background: transparent; border: none; font-size: 7px; font-weight: 700; font-family: %s; letter-spacing: 1px; }" % FONT_STACK
        )
        txt.addWidget(title)
        txt.addWidget(sub)
        txt.addStretch(1)
        logo_row.addLayout(txt, 1)
        root.addLayout(logo_row)
        root.addSpacing(22)
        for key, icon in NAV_ITEMS:
            btn = QPushButton()
            btn.setFixedHeight(54)
            btn.setCursor(Qt.PointingHandCursor)
            inner = QHBoxLayout(btn)
            inner.setContentsMargins(22, 0, 10, 0)
            inner.setSpacing(18)
            ic = QLabel()
            ic.setFixedSize(26, 26)
            ic.setAlignment(Qt.AlignCenter)
            inner.addWidget(ic)
            lab = QLabel(NAV_LABELS[key])
            lab.setAttribute(Qt.WA_TransparentForMouseEvents, True)
            inner.addWidget(lab, 1)
            btn.clicked.connect(lambda _=False, k=key: self.set_active(k))
            root.addSpacing(4)
            root.addWidget(btn)
            self.buttons[key] = (btn, ic, lab, icon)
        root.addStretch(1)
        tag = QLabel(
            '<div style="color:#ffffff; font-size:16px; font-family:%s;">'
            'Ensemble,<br/>transformons<br/>les id\u00e9es en <b style="color:#3fa9ff;">impact !</b></div>' % FONT_STACK
        )
        tag.setContentsMargins(48, 0, 0, 0)
        tag.setAttribute(Qt.WA_TranslucentBackground, True)
        root.addWidget(tag)
        root.addSpacing(86)
        self.refresh()

    def set_active(self, key):
        self.active = key
        self.refresh()

    def refresh(self):
        for key, (btn, ic, lab, icon) in self.buttons.items():
            is_active = (key == self.active)
            icol = "#ffffff" if is_active else "#dfe3ff"
            ic.setPixmap(svg_pixmap(icon, icol, 26, 1.7))
            lab.setStyleSheet(
                "QLabel { color: %s; font-size: 15px; font-weight: %s; font-family: %s; background: transparent; }"
                % (icol, "600" if is_active else "500", FONT_STACK)
            )
            if is_active:
                btn.setStyleSheet(
                    "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                    "stop:0 #3b44f0, stop:1 #5a5af5); border: none; border-radius: 14px; text-align: left; }"
                    "QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, "
                    "stop:0 #4a54ff, stop:1 #6a6aff); }"
                )
                glow_shadow(btn, blur=24, dy=6, alpha=0.35)
            else:
                btn.setStyleSheet(
                    "QPushButton { background: transparent; border: none; border-radius: 14px; text-align: left; }"
                    "QPushButton:hover { background: rgba(255,255,255,0.06); }"
                )
                btn.setGraphicsEffect(None)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing, True)
        g = QLinearGradient(0, 0, 0, self.height())
        g.setColorAt(0, QColor("#0a0e30"))
        g.setColorAt(1, QColor("#0d1142"))
        p.fillRect(self.rect(), g)
        h = self.height()
        w = self.width()
        polys = [
            ([(8, 0), (52, -84), (96, -40), (52, 44)], "#3b44f0", 140),
            ([(52, 44), (96, -40), (150, 0), (106, 84)], "#5a5af5", 120),
            ([(96, -40), (150, -100), (196, -50), (150, 0)], "#7b3fe4", 150),
            ([(8, -100), (52, -150), (96, -110), (52, -50)], "#2f7bf0", 170),
            ([(96, -110), (150, -160), (200, -120), (156, -60)], "#4a54ff", 200),
            ([(150, 0), (200, -50), (244, -10), (200, 50)], "#3fa9ff", 230),
        ]
        p.setPen(Qt.NoPen)
        for pts, color, alpha in polys:
            c = QColor(color)
            c.setAlpha(alpha)
            path = QPainterPath()
            path.moveTo(pts[0][0], h + pts[0][1])
            for x, y in pts[1:]:
                path.lineTo(x, h + y)
            path.closeSubpath()
            p.fillPath(path, c)
        _ = w


class TopBar(QWidget):
    def __init__(self, on_search, parent=None):
        super().__init__(parent)
        self.setFixedHeight(56)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(14)
        search_wrap = QFrame()
        search_wrap.setFixedSize(425, 42)
        search_wrap.setStyleSheet(
            "QFrame { background: #ffffff; border: 1px solid #e8ebf7; border-radius: 21px; }"
        )
        card_shadow(search_wrap, blur=18, dy=4, alpha=0.08)
        srow = QHBoxLayout(search_wrap)
        srow.setContentsMargins(16, 0, 14, 0)
        srow.setSpacing(10)
        srow.addWidget(icon_label("search", PRIMARY, 19, 2.0))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher un participant...")
        self.search.setStyleSheet(
            "QLineEdit { border: none; background: transparent; font-size: 12px; "
            "color: %s; font-family: %s; }" % (INK, FONT_STACK)
        )
        self.search.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.search.textChanged.connect(on_search)
        srow.addWidget(self.search, 1)
        root.addWidget(search_wrap)
        root.addStretch(1)
        root.addWidget(NotifButton("bell"))
        root.addWidget(NotifButton("mail"))
        root.addWidget(AvatarWidget())
        namecol = QVBoxLayout()
        namecol.setSpacing(0)
        namecol.setContentsMargins(0, 6, 0, 6)
        admin = QLabel("Admin")
        admin.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 13px; font-weight: 700; font-family: %s; }" % (INK, FONT_STACK))
        role = QLabel("Administrateur")
        role.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 10px; font-family: %s; }" % (MUTED, FONT_STACK))
        namecol.addWidget(admin)
        namecol.addWidget(role)
        root.addLayout(namecol)
        root.addWidget(icon_label("chevron-down", BODY, 16, 2.2))


class PageHeader(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 6, 0, 6)
        root.setSpacing(12)
        root.addWidget(icon_label("users", "#5b4df6", 40, 1.8))
        txt = QVBoxLayout()
        txt.setSpacing(2)
        title = QLabel("Gestion des participants")
        title.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 22px; font-weight: 800; font-family: %s; }" % (INK, FONT_STACK))
        sub = QLabel("Consultez, g\u00e9rez et suivez tous les participants du HackHet 2026.")
        sub.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 12px; font-family: %s; }" % (BODY, FONT_STACK))
        txt.addWidget(title)
        txt.addWidget(sub)
        root.addLayout(txt, 1)
        add_btn = QPushButton("  Ajouter un participant")
        add_btn.setFixedSize(208, 38)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.setIcon(QIcon(svg_pixmap("plus", "#ffffff", 16, 2.4)))
        add_btn.setStyleSheet(
            "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %s, stop:1 %s); "
            "color: #ffffff; font-size: 13px; font-weight: 600; font-family: %s; "
            "border: none; border-radius: 10px; }"
            "QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a54ff, stop:1 #6d5df7); }"
            % (GRAD_A, GRAD_B, FONT_STACK)
        )
        glow_shadow(add_btn, blur=24, dy=6, alpha=0.35)
        root.addWidget(add_btn)


def stat_card(icon, badge_bg, badge_fg, title, value, caption_html):
    card = QFrame()
    card.setFixedHeight(124)
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    style_card(card)
    outer = QVBoxLayout(card)
    outer.setContentsMargins(14, 12, 14, 10)
    outer.setSpacing(2)
    top = QHBoxLayout()
    top.setSpacing(10)
    top.addWidget(BadgeDot(46, badge_bg, icon, badge_fg, 22))
    tcol = QVBoxLayout()
    tcol.setSpacing(2)
    t = QLabel(title)
    t.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 11px; font-weight: 700; font-family: %s; }" % (INK, FONT_STACK))
    v = QLabel(str(value))
    v.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 30px; font-weight: 800; font-family: %s; }" % (INK, FONT_STACK))
    tcol.addWidget(t)
    tcol.addWidget(v)
    top.addLayout(tcol, 1)
    outer.addLayout(top)
    cap = QLabel(caption_html)
    cap.setAlignment(Qt.AlignCenter)
    cap.setWordWrap(True)
    cap.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 10px; font-family: %s; }" % (MUTED, FONT_STACK))
    outer.addWidget(cap)
    return card


def build_stat_row():
    row = QHBoxLayout()
    row.setSpacing(12)
    row.addWidget(stat_card("users", "#e8e6fb", "#6a5ae0", "Total participants", "120",
        '<span style="color:#16a34a; font-weight:700;">\u2197 +12%</span> par rapport \u00e0 l\u2019ann\u00e9e derni\u00e8re'))
    row.addWidget(stat_card("user", "#dcf6ec", GREEN, "\u00c9tudiants", "72",
        '<b style="color:#16a34a;">60%</b> du total'))
    row.addWidget(stat_card("briefcase", "#ffe1ec", PINK, "Enseignants", "18",
        '<b style="color:%s;">15%%</b> du total' % PINK))
    row.addWidget(stat_card("user", "#dcebff", BLUE, "Professionnels", "14",
        '<b style="color:%s;">12%%</b> du total' % BLUE))
    row.addWidget(stat_card("users", "#fff0d0", ORANGE, "Autres", "16",
        '<b style="color:%s;">13%%</b> du total' % ORANGE))
    return row


class CheckBox(QPushButton):
    def __init__(self, checked=False, parent=None):
        super().__init__(parent)
        self._checked = bool(checked)
        self.setFixedSize(16, 16)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.toggle_state)
        self._paint_style()

    def toggle_state(self):
        self._checked = not self._checked
        self._paint_style()

    def isChecked(self):
        return self._checked

    def setChecked(self, v):
        self._checked = bool(v)
        self._paint_style()

    def _paint_style(self):
        if self._checked:
            self.setStyleSheet(
                "QPushButton { background: #4338f0; border: 1.5px solid #4338f0; border-radius: 5px; }"
                "QPushButton:hover { background: #4f46e5; }"
            )
            self.setIcon(QIcon(svg_pixmap("check", "#ffffff", 11, 3.0)))
        else:
            self.setStyleSheet(
                "QPushButton { background: #ffffff; border: 1.5px solid #cbd0e6; border-radius: 5px; }"
                "QPushButton:hover { border-color: #4338f0; }"
            )
            self.setIcon(QIcon())


class ActionButton(QPushButton):
    def __init__(self, icon, parent=None):
        super().__init__(parent)
        self.setFixedSize(28, 28)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(svg_pixmap(icon, "#4a5278", 14, 2.0)))
        self.setStyleSheet(
            "QPushButton { background: #ffffff; border: 1px solid #e0e4f4; border-radius: 14px; }"
            "QPushButton:hover { background: #eef0ff; }"
        )


class ParticipantsCard(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        style_card(self)
        self.page = 1
        self.sort_mode = 0
        self.sort_touched = False
        self.role_filter = "Tous les r\u00f4les"
        self.team_filter = "Toutes les \u00e9quipes"
        self.query = ""
        root = QVBoxLayout(self)
        root.setContentsMargins(15, 15, 15, 15)
        root.setSpacing(12)
        # ---- toolbar ----
        bar = QHBoxLayout()
        bar.setSpacing(10)
        search_wrap = QFrame()
        search_wrap.setFixedHeight(36)
        search_wrap.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        search_wrap.setStyleSheet(
            "QFrame { background: #ffffff; border: 1px solid #e3e6f5; border-radius: 9px; }"
        )
        srow = QHBoxLayout(search_wrap)
        srow.setContentsMargins(12, 0, 10, 0)
        srow.setSpacing(8)
        srow.addWidget(icon_label("search", PRIMARY, 16, 2.2))
        self.search = QLineEdit()
        self.search.setPlaceholderText("Rechercher par nom, email, \u00e9cole...")
        self.search.setStyleSheet(
            "QLineEdit { border: none; background: transparent; font-size: 11px; color: %s; font-family: %s; }" % (INK, FONT_STACK)
        )
        self.search.textChanged.connect(self._on_query)
        srow.addWidget(self.search, 1)
        bar.addWidget(search_wrap, 1)
        self.role_combo = self._combo(["Tous les r\u00f4les", "\u00c9tudiant", "Enseignant", "Professionnel", "Autre"], 128)
        self.team_combo = self._combo(["Toutes les \u00e9quipes", "GreenTech", "CodeCraft", "PixelForce"], 144)
        self.sort_combo = self._combo(["Trier par : Nom (A-Z)", "Trier par : Nom (Z-A)", "Trier par : R\u00f4le"], 173)
        self.role_combo.currentTextChanged.connect(self._on_role)
        self.team_combo.currentTextChanged.connect(self._on_team)
        self.sort_combo.currentIndexChanged.connect(self._on_sort)
        bar.addWidget(self.role_combo)
        bar.addWidget(self.team_combo)
        bar.addWidget(self.sort_combo)
        sliders = QPushButton()
        sliders.setFixedSize(36, 36)
        sliders.setCursor(Qt.PointingHandCursor)
        sliders.setIcon(QIcon(svg_pixmap("sliders", PRIMARY, 17, 2.0)))
        sliders.setStyleSheet(
            "QPushButton { background: #ffffff; border: 1px solid #e3e6f5; border-radius: 9px; }"
            "QPushButton:hover { background: #eef0ff; }"
        )
        bar.addWidget(sliders)
        root.addLayout(bar)
        # ---- table frame ----
        self.table = QFrame()
        self.table.setStyleSheet("QFrame { background: #ffffff; border: 1px solid #edf0fb; border-radius: 12px; }")
        troot = QVBoxLayout(self.table)
        troot.setContentsMargins(0, 0, 0, 0)
        troot.setSpacing(0)
        header = QWidget()
        header.setFixedHeight(38)
        header.setStyleSheet("QWidget { background: #f4f5fd; border: none; border-bottom: 1px solid #edf0fb; }")
        hrow = QHBoxLayout(header)
        hrow.setContentsMargins(14, 0, 14, 0)
        hrow.setSpacing(8)
        self.header_cb = CheckBox()
        self.header_cb.setFixedSize(16, 16)
        hrow.addWidget(self.header_cb, COL_STRETCH[0])
        for i, h in enumerate(["Nom & Pr\u00e9nom", "Email", "R\u00f4le", "\u00c9quipe", "Statut", "Actions"]):
            lab = QLabel(h)
            lab.setStyleSheet("QLabel { color: #2b3358; font-size: 11px; font-weight: 700; font-family: %s; background: transparent; border: none; }" % FONT_STACK)
            lab.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            align = Qt.AlignCenter if h == "Actions" else Qt.AlignLeft | Qt.AlignVCenter
            lab.setAlignment(align)
            hrow.addWidget(lab, COL_STRETCH[i + 1])
        troot.addWidget(header)
        rows_wrap = QWidget()
        rows_wrap.setStyleSheet("QWidget { background: transparent; border: none; }")
        self.rows_host = QVBoxLayout(rows_wrap)
        self.rows_host.setSpacing(0)
        self.rows_host.setContentsMargins(0, 0, 0, 0)
        troot.addWidget(rows_wrap)
        self.table.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        root.addWidget(self.table, 0)
        # ---- footer ----
        foot = QHBoxLayout()
        foot.setContentsMargins(2, 0, 2, 0)
        self.count_label = QLabel("")
        self.count_label.setStyleSheet("QLabel { color: %s; font-size: 10px; font-family: %s; }" % (BODY, FONT_STACK))
        foot.addWidget(self.count_label, 1)
        pagi = QHBoxLayout()
        pagi.setSpacing(8)
        self.page_buttons = {}
        prev = self._page_btn("<", "prev")
        prev.clicked.connect(lambda: self.set_page(max(1, self.page - 1)))
        pagi.addWidget(prev)
        for pnum in [1, 2, 3, 4, 5]:
            b = self._page_btn(str(pnum), pnum)
            b.clicked.connect(lambda _=False, n=pnum: self.set_page(n))
            pagi.addWidget(b)
            self.page_buttons[pnum] = b
        dots = QLabel("\u2026")
        dots.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 12px; }" % BODY)
        pagi.addWidget(dots)
        last = self._page_btn("12", 12)
        last.clicked.connect(lambda: self.set_page(12))
        pagi.addWidget(last)
        self.page_buttons[12] = last
        nxt = self._page_btn(">", "next")
        nxt.clicked.connect(lambda: self.set_page(min(12, self.page + 1)))
        pagi.addWidget(nxt)
        self.prev_btn, self.next_btn = prev, nxt
        foot.addLayout(pagi)
        root.addLayout(foot)
        self.refresh()

    def _combo(self, items, width):
        combo = QComboBox()
        combo.addItems(items)
        combo.setFixedHeight(36)
        combo.setFixedWidth(width)
        combo.setCursor(Qt.PointingHandCursor)
        url = get_chevron_url()
        combo.setStyleSheet(
            "QComboBox { background: #ffffff; border: 1px solid #e3e6f5; border-radius: 9px; "
            "font-size: 11px; color: #4a5278; font-family: %s; padding-left: 12px; padding-right: 28px; }" % FONT_STACK +
            "QComboBox:hover { border-color: #c9cdf5; }" +
            "QComboBox::drop-down { border: none; width: 26px; }" +
            "QComboBox::down-arrow { image: url(%s); width: 12px; height: 12px; }" % url +
            "QComboBox QAbstractItemView { background: #ffffff; border: 1px solid #e3e6f5; "
            "selection-background-color: #eef0ff; selection-color: #3f46f0; outline: none; font-size: 11px; }"
        )
        return combo

    def _page_btn(self, text, key):
        b = QPushButton(text)
        b.setFixedSize(26, 26)
        b.setCursor(Qt.PointingHandCursor)
        if text in ("<", ">"):
            icon = "chevron-left" if text == "<" else "chevron-right"
            b.setText("")
            b.setIcon(QIcon(svg_pixmap(icon, PRIMARY, 13, 2.4)))
        return b

    def _paint_pages(self):
        for key, b in self.page_buttons.items():
            if key == self.page:
                b.setStyleSheet(
                    "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %s, stop:1 %s); "
                    "color: #ffffff; font-size: 11px; font-weight: 700; border: none; border-radius: 8px; }" % (GRAD_A, GRAD_B)
                )
            else:
                b.setStyleSheet(
                    "QPushButton { background: #ffffff; border: 1px solid #e3e6f5; border-radius: 8px; "
                    "color: #4a5278; font-size: 11px; }"
                    "QPushButton:hover { background: #eef0ff; }"
                )
        for b in (self.prev_btn, self.next_btn):
            b.setStyleSheet(
                "QPushButton { background: #ffffff; border: 1px solid #e3e6f5; border-radius: 8px; }"
                "QPushButton:hover { background: #eef0ff; }"
            )

    def set_page(self, n):
        self.page = int(n)
        self._paint_pages()

    def set_query(self, q):
        self.query = q or ""
        try:
            self.search.blockSignals(True)
            if self.search.text() != self.query:
                self.search.setText(self.query)
        finally:
            self.search.blockSignals(False)
        self.refresh()

    def _on_query(self, q):
        self.query = q or ""
        self.refresh()

    def _on_role(self, t):
        self.role_filter = t
        self.refresh()

    def _on_team(self, t):
        self.team_filter = t
        self.refresh()

    def _on_sort(self, idx):
        self.sort_mode = int(idx)
        self.sort_touched = True
        self.refresh()

    def visible_rows(self):
        q = norm(self.query)
        out = []
        for d in PARTICIPANTS:
            if q and q not in norm(d["name"] + " " + d["email"] + " " + d["school"]):
                continue
            if self.role_filter not in ("Tous les r\u00f4les", "", None):
                if norm(ROLE_DISPLAY[d["role"]]) != norm(self.role_filter):
                    continue
            if self.team_filter not in ("Toutes les \u00e9quipes", "", None):
                if (d["team"] or "") != self.team_filter:
                    continue
            out.append(d)
        if self.sort_touched:
            if self.sort_mode == 0:
                out = sorted(out, key=lambda d: norm(d["name"]))
            elif self.sort_mode == 1:
                out = sorted(out, key=lambda d: norm(d["name"]), reverse=True)
            elif self.sort_mode == 2:
                out = sorted(out, key=lambda d: (norm(ROLE_DISPLAY[d["role"]]), norm(d["name"])))
        return out

    def refresh(self):
        while self.rows_host.count():
            item = self.rows_host.takeAt(0)
            w = item.widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()
        rows = self.visible_rows()
        for idx, d in enumerate(rows):
            row = QWidget()
            row.setFixedHeight(49)
            border = "border-bottom: 1px solid #eef0fa;" if idx < len(rows) - 1 else "border-bottom: none;"
            row.setStyleSheet("QWidget { background: #ffffff; %s } QWidget:hover { background: #fafbff; }" % border)
            h = QHBoxLayout(row)
            h.setContentsMargins(14, 0, 14, 0)
            h.setSpacing(8)
            h.addWidget(CheckBox(), COL_STRETCH[0])
            # name cell
            name_cell = QWidget()
            name_cell.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            name_cell.setStyleSheet("QWidget { background: transparent; border: none; }")
            nl = QHBoxLayout(name_cell)
            nl.setContentsMargins(0, 0, 0, 0)
            nl.setSpacing(10)
            nl.addWidget(AvatarBadge(d["initials"], d["bg"], d["fg"]))
            ncol = QVBoxLayout()
            ncol.setSpacing(0)
            nm = QLabel(d["name"])
            nm.setStyleSheet("QLabel { color: %s; font-size: 12px; font-weight: 600; font-family: %s; background: transparent; border: none; }" % (INK, FONT_STACK))
            sc = QLabel(d["school"])
            sc.setStyleSheet("QLabel { color: %s; font-size: 9px; font-family: %s; background: transparent; border: none; }" % (MUTED, FONT_STACK))
            ncol.addWidget(nm)
            ncol.addWidget(sc)
            nl.addLayout(ncol, 1)
            h.addWidget(name_cell, COL_STRETCH[1])
            em = QLabel(d["email"])
            em.setStyleSheet("QLabel { color: %s; font-size: 10px; font-family: %s; background: transparent; border: none; }" % (BODY, FONT_STACK))
            em.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            h.addWidget(em, COL_STRETCH[2])
            bg, fg = ROLE_STYLE[d["role"]]
            rp = pill(ROLE_DISPLAY[d["role"]], bg, fg)
            rwrap = QWidget()
            rwrap.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            rwrap.setStyleSheet("QWidget { background: transparent; border: none; }")
            rl = QHBoxLayout(rwrap)
            rl.setContentsMargins(0, 0, 0, 0)
            rl.addWidget(rp)
            rl.addStretch(1)
            h.addWidget(rwrap, COL_STRETCH[3])
            team_txt = d["team"] if d["team"] else "\u2014"
            tm = QLabel(team_txt)
            tm.setStyleSheet("QLabel { color: #4a5278; font-size: 11px; font-family: %s; background: transparent; border: none; }" % FONT_STACK)
            tm.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            h.addWidget(tm, COL_STRETCH[4])
            sbg, sfg = STATUS_STYLE[d["status"]]
            sp = pill(d["status"], sbg, sfg)
            swrap = QWidget()
            swrap.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            swrap.setStyleSheet("QWidget { background: transparent; border: none; }")
            sl = QHBoxLayout(swrap)
            sl.setContentsMargins(0, 0, 0, 0)
            sl.addWidget(sp)
            sl.addStretch(1)
            h.addWidget(swrap, COL_STRETCH[5])
            acts = QWidget()
            acts.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
            acts.setStyleSheet("QWidget { background: transparent; border: none; }")
            al = QHBoxLayout(acts)
            al.setContentsMargins(0, 0, 0, 0)
            al.setSpacing(6)
            al.setAlignment(Qt.AlignCenter)
            al.addWidget(ActionButton("eye"))
            al.addWidget(ActionButton("edit"))
            al.addWidget(ActionButton("trash"))
            h.addWidget(acts, COL_STRETCH[6])
            self.rows_host.addWidget(row)
        n = len(rows)
        if n == 0:
            self.count_label.setText("Affichage de 0 \u00e0 0 sur 120 participants")
        else:
            self.count_label.setText("Affichage de 1 \u00e0 %d sur 120 participants" % n)
        self._paint_pages()


def card_header(icon, title, right=None, badge=False, icon_bg="#5b4df6"):
    head = QHBoxLayout()
    head.setSpacing(8)
    head.setContentsMargins(0, 0, 0, 0)
    if badge:
        b = BadgeDot(24, icon_bg, icon, "#ffffff", 13)
        head.addWidget(b)
    else:
        head.addWidget(icon_label(icon, PRIMARY, 20, 2.0))
    t = QLabel(title)
    t.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 13px; font-weight: 700; font-family: %s; }" % (INK, FONT_STACK))
    head.addWidget(t, 1)
    if right is not None:
        head.addWidget(right)
    wrap = transparent_widget(QWidget())
    wrap.setLayout(head)
    return wrap


def voir_tout():
    b = QPushButton("Voir tout")
    b.setCursor(Qt.PointingHandCursor)
    b.setIcon(QIcon(svg_pixmap("arrow-right", PRIMARY, 12, 2.2)))
    b.setLayoutDirection(Qt.RightToLeft)
    b.setStyleSheet(
        "QPushButton { color: %s; font-size: 10px; font-weight: 600; font-family: %s; "
        "border: none; background: transparent; }" % (PRIMARY, FONT_STACK)
    )
    return b


def collapse_btn():
    b = QPushButton()
    b.setFixedSize(20, 20)
    b.setCursor(Qt.PointingHandCursor)
    b.setStyleSheet("QPushButton { border: none; background: transparent; }")
    return b


def filter_checkbox(text, checked=False):
    row = QHBoxLayout()
    row.setSpacing(7)
    row.setContentsMargins(0, 0, 0, 0)
    cb = CheckBox(checked)
    lab = QLabel(text)
    lab.setStyleSheet("QLabel { color: %s; font-size: 11px; font-family: %s; }" % (BODY, FONT_STACK))
    row.addWidget(cb)
    row.addWidget(lab, 1)
    wrap = transparent_widget(QWidget())
    wrap.setLayout(row)
    return wrap, cb


def build_filters_card():
    card = QFrame()
    style_card(card)
    root = QVBoxLayout(card)
    root.setContentsMargins(15, 13, 15, 15)
    root.setSpacing(10)
    chev = collapse_btn()
    chev.setIcon(QIcon(svg_pixmap("chevron-up", BODY, 14, 2.2)))
    root.addWidget(card_header("filter", "Filtres avanc\u00e9s", chev))
    body = QWidget()
    bl = QVBoxLayout(body)
    bl.setContentsMargins(0, 0, 0, 0)
    bl.setSpacing(8)
    st = QLabel("\u00c9tat du compte")
    st.setStyleSheet("QLabel { color: %s; font-size: 11px; font-family: %s; }" % (BODY, FONT_STACK))
    bl.addWidget(st)
    cbs = QHBoxLayout()
    cbs.setSpacing(14)
    w1, cb_actif = filter_checkbox("Actif", True)
    w2, cb_inactif = filter_checkbox("Inactif", False)
    cbs.addWidget(w1)
    cbs.addWidget(w2)
    cbs.addStretch(1)
    bl.addLayout(cbs)
    for lab_text, items in [("Ann\u00e9e de participation", ["Toutes", "2026", "2025", "2024"]), ("\u00c9quipe", ["Toutes", "GreenTech", "CodeCraft", "PixelForce"])]:
        lab = QLabel(lab_text)
        lab.setStyleSheet("QLabel { color: %s; font-size: 11px; font-family: %s; }" % (BODY, FONT_STACK))
        bl.addWidget(lab)
        combo = QComboBox()
        combo.addItems(items)
        combo.setFixedHeight(34)
        combo.setCursor(Qt.PointingHandCursor)
        url = get_chevron_url()
        combo.setStyleSheet(
            "QComboBox { background: #ffffff; border: 1px solid #e3e6f5; border-radius: 9px; "
            "font-size: 11px; color: #4a5278; font-family: %s; padding-left: 12px; padding-right: 28px; }" % FONT_STACK +
            "QComboBox::drop-down { border: none; width: 26px; }" +
            "QComboBox::down-arrow { image: url(%s); width: 12px; height: 12px; }" % url +
            "QComboBox QAbstractItemView { background: #ffffff; border: 1px solid #e3e6f5; "
            "selection-background-color: #eef0ff; selection-color: #3f46f0; outline: none; font-size: 11px; }"
        )
        bl.addWidget(combo)
    lab = QLabel("Comp\u00e9tences")
    lab.setStyleSheet("QLabel { color: %s; font-size: 11px; font-family: %s; }" % (BODY, FONT_STACK))
    bl.addWidget(lab)
    comp = QLineEdit()
    comp.setFixedHeight(32)
    comp.setPlaceholderText("Ex: C++, Design, R\u00e9seaux...")
    comp.setStyleSheet(
        "QLineEdit { background: #ffffff; border: 1px solid #e3e6f5; border-radius: 9px; "
        "font-size: 11px; color: %s; font-family: %s; padding-left: 12px; }" % (INK, FONT_STACK)
    )
    bl.addWidget(comp)
    brows = QHBoxLayout()
    brows.setSpacing(8)
    apply_btn = QPushButton("Appliquer les filtres")
    apply_btn.setFixedHeight(32)
    apply_btn.setCursor(Qt.PointingHandCursor)
    apply_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    apply_btn.setStyleSheet(
        "QPushButton { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 %s, stop:1 %s); "
        "color: #ffffff; font-size: 11px; font-weight: 700; font-family: %s; border: none; border-radius: 8px; }"
        "QPushButton:hover { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #4a54ff, stop:1 #6d5df7); }"
        % (GRAD_A, GRAD_B, FONT_STACK)
    )
    reset_btn = QPushButton("R\u00e9initialiser")
    reset_btn.setFixedHeight(32)
    reset_btn.setCursor(Qt.PointingHandCursor)
    reset_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
    reset_btn.setStyleSheet(
        "QPushButton { background: #eef0ff; color: %s; font-size: 11px; font-weight: 700; "
        "font-family: %s; border: none; border-radius: 8px; }"
        "QPushButton:hover { background: #e2e7ff; }" % (PRIMARY, FONT_STACK)
    )
    brows.addWidget(apply_btn, 5)
    brows.addWidget(reset_btn, 4)
    bl.addLayout(brows)
    root.addWidget(body)
    def _toggle():
        vis = not body.isVisible()
        body.setVisible(vis)
        chev.setIcon(QIcon(svg_pixmap("chevron-up" if vis else "chevron-down", BODY, 14, 2.2)))
    chev.clicked.connect(_toggle)
    def _reset():
        cb_actif.setChecked(True)
        cb_inactif.setChecked(False)
        comp.clear()
    reset_btn.clicked.connect(_reset)
    return card


def build_role_card():
    card = QFrame()
    style_card(card)
    root = QVBoxLayout(card)
    root.setContentsMargins(15, 13, 15, 15)
    root.setSpacing(10)
    chev = collapse_btn()
    chev.setIcon(QIcon(svg_pixmap("chevron-up", BODY, 14, 2.2)))
    root.addWidget(card_header("pie", "R\u00e9partition par r\u00f4le", chev, badge=True))
    body = QWidget()
    bl = QHBoxLayout(body)
    bl.setContentsMargins(0, 0, 0, 0)
    bl.setSpacing(12)
    donut = DonutWidget([(72, "#4f46e5"), (18, "#14b8a6"), (14, "#fbbf24"), (16, "#f59e0b")])
    bl.addWidget(donut)
    legend = QVBoxLayout()
    legend.setSpacing(10)
    legend.setContentsMargins(0, 8, 0, 8)
    for label, pct, count, color in [
        ("\u00c9tudiants", "60%", "72", "#4f46e5"), ("Enseignants", "15%", "18", "#14b8a6"),
        ("Professionnels", "12%", "14", "#fbbf24"), ("Autres", "13%", "16", "#f59e0b")]:
        row = QHBoxLayout()
        row.setSpacing(6)
        dot = QLabel()
        dot.setFixedSize(8, 8)
        dot.setStyleSheet("QLabel { background: %s; border-radius: 4px; }" % color)
        row.addWidget(dot)
        lab = QLabel(label)
        lab.setStyleSheet("QLabel { color: %s; font-size: 10px; font-family: %s; }" % (BODY, FONT_STACK))
        lab.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        row.addWidget(lab, 1)
        pc = QLabel(pct)
        pc.setStyleSheet("QLabel { color: %s; background: transparent; border: none; font-size: 10px; font-weight: 700; font-family: %s; }" % (INK, FONT_STACK))
        row.addWidget(pc)
        ct = QLabel(count)
        ct.setFixedWidth(18)
        ct.setAlignment(Qt.AlignRight)
        ct.setStyleSheet("QLabel { color: %s; font-size: 10px; font-family: %s; }" % (BODY, FONT_STACK))
        row.addWidget(ct)
        legend.addLayout(row)
    legend.addStretch(1)
    bl.addLayout(legend, 1)
    root.addWidget(body)
    chev.clicked.connect(lambda: (body.setVisible(not body.isVisible()), chev.setIcon(QIcon(svg_pixmap("chevron-up" if body.isVisible() else "chevron-down", BODY, 14, 2.2)))))
    return card


def build_skills_card():
    card = QFrame()
    style_card(card)
    root = QVBoxLayout(card)
    root.setContentsMargins(15, 13, 15, 15)
    root.setSpacing(9)
    root.addWidget(card_header("cpu", "Comp\u00e9tences principales", voir_tout(), badge=True))
    skills = [
        ("C++", 42, "code", ("#4f46e5", "#6d5ff7")),
        ("D\u00e9veloppement Web", 35, "globe", ("#2b8cf0", "#38b6ff")),
        ("Intelligence Artificielle", 28, "cpu", ("#14b8a6", "#2dd4bf")),
        ("Design UI/UX", 21, "pen", ("#f59e0b", "#fbbf24")),
        ("R\u00e9seaux", 18, "share", ("#ec4899", "#f472b6")),
    ]
    for label, count, icon, grad in skills:
        row = QHBoxLayout()
        row.setSpacing(8)
        row.addWidget(BadgeDot(18, grad, icon, "#ffffff", 10))
        col = QVBoxLayout()
        col.setSpacing(3)
        top = QHBoxLayout()
        top.setContentsMargins(0, 0, 0, 0)
        lab = QLabel(label)
        lab.setStyleSheet("QLabel { color: %s; font-size: 10px; font-weight: 600; font-family: %s; }" % (INK, FONT_STACK))
        top.addWidget(lab, 1)
        ct = QLabel(str(count))
        ct.setStyleSheet("QLabel { color: %s; font-size: 10px; font-weight: 700; font-family: %s; }" % (INK, FONT_STACK))
        top.addWidget(ct)
        col.addLayout(top)
        col.addWidget(ProgressWidget(count, 51, grad))
        row.addLayout(col, 1)
        wrap = transparent_widget(QWidget())
        wrap.setLayout(row)
        root.addWidget(wrap)
    return card


def build_top_teams_card():
    card = QFrame()
    style_card(card)
    root = QVBoxLayout(card)
    root.setContentsMargins(15, 13, 15, 15)
    root.setSpacing(10)
    root.addWidget(card_header("trophy", "Top 3 \u00e9quipes", voir_tout()))
    tiles = QHBoxLayout()
    tiles.setSpacing(8)
    teams = [
        ("GreenTech", "92 pts", "leaf", "#fff7e0", "#f4e2ae", "#d99a14", "#f5a623", "1"),
        ("CodeCraft", "78 pts", "code", "#eaf1ff", "#cfdcf8", "#4a6fe0", "#5b8def", "2"),
        ("PixelForce", "64 pts", "gamepad", "#ffe9ef", "#f8cfda", "#e0527a", "#ef6a6a", "3"),
    ]
    for name, pts, icon, bg, border, text, rank_bg, rank in teams:
        cell = QWidget()
        cell.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        cell_lay = QVBoxLayout(cell)
        cell_lay.setContentsMargins(0, 0, 0, 0)
        cell_lay.setSpacing(-8)
        rank_row = QHBoxLayout()
        rank_row.setContentsMargins(0, 0, 0, 0)
        rank_row.setAlignment(Qt.AlignCenter)
        rank_lab = QLabel(rank)
        rank_lab.setFixedSize(16, 16)
        rank_lab.setAlignment(Qt.AlignCenter)
        rank_lab.setStyleSheet(
            "QLabel { background: %s; color: #ffffff; font-size: 9px; font-weight: 700; border-radius: 8px; }" % rank_bg
        )
        rank_row.addWidget(rank_lab)
        rank_host = QWidget()
        rank_host.setLayout(rank_row)
        rank_host.setStyleSheet("QWidget { background: transparent; border: none; }")
        cell_lay.addWidget(rank_host)
        tile = QFrame()
        tile.setFixedHeight(68)
        tile.setStyleSheet("QFrame { background: %s; border: 1px solid %s; border-radius: 10px; }" % (bg, border))
        lay = QVBoxLayout(tile)
        lay.setContentsMargins(4, 12, 4, 6)
        lay.setSpacing(1)
        lay.setAlignment(Qt.AlignCenter)
        wcirc = BadgeDot(24, "#ffffff", icon, text, 13)
        card_shadow(wcirc, blur=10, dy=2, alpha=0.12)
        cent = QHBoxLayout()
        cent.setAlignment(Qt.AlignCenter)
        cent.setContentsMargins(0, 0, 0, 0)
        cent.addWidget(wcirc)
        cw = QWidget()
        cw.setLayout(cent)
        cw.setStyleSheet("QWidget { background: transparent; border: none; }")
        lay.addWidget(cw)
        nm = QLabel(name)
        nm.setAlignment(Qt.AlignCenter)
        nm.setStyleSheet("QLabel { color: %s; font-size: 9px; font-weight: 600; font-family: %s; background: transparent; border: none; }" % (text, FONT_STACK))
        lay.addWidget(nm)
        pl = QLabel(pts)
        pl.setAlignment(Qt.AlignCenter)
        pl.setStyleSheet("QLabel { color: %s; font-size: 9px; font-family: %s; background: transparent; border: none; }" % (text, FONT_STACK))
        lay.addWidget(pl)
        cell_lay.addWidget(tile)
        rank_host.raise_()
        tiles.addWidget(cell)
    wrap = transparent_widget(QWidget())
    wrap.setLayout(tiles)
    root.addWidget(wrap)
    return card


def build_matching_banner():
    card = QFrame()
    card.setStyleSheet(
        "QFrame { background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #eef0ff, stop:1 #f5ebff); "
        "border: 1px solid #e0e4fb; border-radius: 14px; }"
    )
    card_shadow(card)
    root = QHBoxLayout(card)
    root.setContentsMargins(14, 14, 12, 14)
    root.setSpacing(10)
    root.addWidget(BadgeDot(46, ("#3b6cf0", "#7a4cf5"), "bulb", "#ffffff", 22))
    col = QVBoxLayout()
    col.setSpacing(3)
    t = QLabel("Matching intelligent")
    t.setStyleSheet("QLabel { color: %s; font-size: 12px; font-weight: 700; font-family: %s; }" % (INK, FONT_STACK))
    col.addWidget(t)
    d = QLabel("Trouvez les \u00e9quipes qui correspondent le mieux aux comp\u00e9tences et aux int\u00e9r\u00eats des participants.")
    d.setWordWrap(True)
    d.setStyleSheet("QLabel { color: %s; font-size: 9px; font-family: %s; }" % (BODY, FONT_STACK))
    col.addWidget(d)
    root.addLayout(col, 1)
    root.addWidget(icon_label("arrow-right", PRIMARY, 18, 2.2))
    return card


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HackHet \u2013 Gestion des participants")
        self.resize(1536, 1024)
        self.setMinimumSize(1180, 720)
        central = QWidget()
        central.setObjectName("centralRoot")
        central.setStyleSheet("QWidget#centralRoot { background: %s; }" % PAGE_BG)
        self.setCentralWidget(central)
        outer = QHBoxLayout(central)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(Sidebar())
        scroll = QScrollArea()
        scroll.setFrameShape(QScrollArea.NoFrame)
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setStyleSheet("QScrollArea { background: %s; border: none; }" % PAGE_BG)
        outer.addWidget(scroll, 1)
        page = QWidget()
        page.setObjectName("pageRoot")
        page.setStyleSheet("QWidget#pageRoot { background: %s; }" % PAGE_BG)
        scroll.setWidget(page)
        pl = QVBoxLayout(page)
        pl.setContentsMargins(18, 14, 24, 14)
        pl.setSpacing(12)
        self.parts = ParticipantsCard()
        top = TopBar(on_search=self.parts.set_query)
        pl.addWidget(top)
        pl.addWidget(PageHeader())
        cols = QHBoxLayout()
        cols.setSpacing(14)
        main_col = QVBoxLayout()
        main_col.setSpacing(14)
        stat_row = build_stat_row()
        stat_host = QWidget()
        stat_host.setStyleSheet("QWidget { background: transparent; border: none; }")
        stat_host.setLayout(stat_row)
        main_col.addWidget(stat_host)
        main_col.addWidget(self.parts, 0)
        main_col.addStretch(1)
        cols.addLayout(main_col, 1)
        right = QVBoxLayout()
        right.setSpacing(14)
        right.addWidget(build_filters_card())
        right.addWidget(build_role_card())
        right.addWidget(build_skills_card())
        right.addWidget(build_top_teams_card())
        right.addWidget(build_matching_banner())
        right.addStretch(1)
        right_host = QWidget()
        right_host.setStyleSheet("QWidget { background: transparent; border: none; }")
        right_host.setFixedWidth(322)
        right_host.setLayout(right)
        right_host.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        cols.addWidget(right_host)
        cols.setStretch(0, 1)
        cols.setStretch(1, 0)
        pl.addLayout(cols, 1)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("HackHet")
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
