"""Application logo widget."""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtSvgWidgets import QSvgWidget
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from learning_materials.constants import LOGO_PNG_PATH, LOGO_SVG_PATH

_FALLBACK_ASPECT = 120 / 148


def _make_background_transparent(image: QImage, *, threshold: int = 42) -> QImage:
    result = image.convertToFormat(QImage.Format.Format_ARGB32)
    for y in range(result.height()):
        for x in range(result.width()):
            color = result.pixelColor(x, y)
            if color.red() <= threshold and color.green() <= threshold and color.blue() <= threshold:
                color.setAlpha(0)
                result.setPixelColor(x, y, color)
    return result


def _trim_transparent_edges(pixmap: QPixmap) -> QPixmap:
    image = pixmap.toImage()
    width = image.width()
    height = image.height()
    left = width
    top = height
    right = 0
    bottom = 0
    for y in range(height):
        for x in range(width):
            if image.pixelColor(x, y).alpha() > 0:
                left = min(left, x)
                top = min(top, y)
                right = max(right, x)
                bottom = max(bottom, y)
    if right <= left or bottom <= top:
        return pixmap
    return QPixmap.fromImage(image.copy(left, top, right - left + 1, bottom - top + 1))


def _load_logo_pixmap(path: Path) -> QPixmap:
    pixmap = QPixmap(str(path))
    if pixmap.isNull():
        return pixmap
    image = _make_background_transparent(pixmap.toImage())
    return _trim_transparent_edges(QPixmap.fromImage(image))


def _logo_aspect(path: Path, pixmap: QPixmap | None = None) -> float:
    if pixmap is not None and not pixmap.isNull() and pixmap.height() > 0:
        return pixmap.width() / pixmap.height()
    if path.suffix.lower() == ".svg":
        return _FALLBACK_ASPECT
    loaded = QPixmap(str(path))
    if loaded.isNull() or loaded.height() == 0:
        return _FALLBACK_ASPECT
    return loaded.width() / loaded.height()


def logo_dimensions(height: int, *, aspect: float = _FALLBACK_ASPECT) -> tuple[int, int]:
    width = max(1, round(height * aspect))
    return width, height


def _resolve_logo_path() -> Path:
    if LOGO_PNG_PATH.exists():
        return LOGO_PNG_PATH
    return LOGO_SVG_PATH


class AppLogo(QWidget):
    """Brand mark from exported Figma assets (`logo.png` or `logo.svg`)."""

    def __init__(self, height: int = 100, *, centered: bool = True) -> None:
        super().__init__()
        self.setObjectName("appLogo")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        if centered:
            layout.addStretch()

        logo_path = _resolve_logo_path()
        if logo_path.suffix.lower() == ".png":
            pixmap = _load_logo_pixmap(logo_path)
            aspect = _logo_aspect(logo_path, pixmap)
            width, logo_height = logo_dimensions(height, aspect=aspect)
            label = QLabel()
            label.setPixmap(
                pixmap.scaled(
                    width,
                    logo_height,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation,
                )
            )
            label.setFixedSize(width, logo_height)
            label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            widget: QWidget = label
        else:
            aspect = _logo_aspect(logo_path)
            width, logo_height = logo_dimensions(height, aspect=aspect)
            svg = QSvgWidget(str(logo_path))
            svg.setFixedSize(width, logo_height)
            svg.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            widget = svg

        layout.addWidget(widget, alignment=Qt.AlignmentFlag.AlignVCenter)

        if centered:
            layout.addStretch()
