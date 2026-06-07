"""Hover animations and visual polish for interactive widgets."""

from __future__ import annotations

from PyQt6.QtCore import QEasingCurve, QObject, QPropertyAnimation, QEvent
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import (
    QAbstractButton,
    QGraphicsDropShadowEffect,
    QTableWidget,
    QWidget,
)

from learning_materials.theme import current_palette


class _ButtonHoverEffect(QObject):
    def __init__(self, button: QAbstractButton) -> None:
        super().__init__(button)
        self._button = button
        self._animation: QPropertyAnimation | None = None
        palette = current_palette()
        self._effect = QGraphicsDropShadowEffect(button)
        self._effect.setOffset(0, 2)
        self._effect.setBlurRadius(0)
        self._effect.setColor(QColor(palette.primary))
        button.setGraphicsEffect(self._effect)
        button.installEventFilter(self)

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        if watched is not self._button:
            return False
        if event.type() == QEvent.Type.Enter:
            self._animate_blur(14)
        elif event.type() == QEvent.Type.Leave:
            self._animate_blur(0)
        return False

    def _animate_blur(self, target: int) -> None:
        palette = current_palette()
        self._effect.setColor(QColor(palette.primary))
        if self._animation is not None:
            self._animation.stop()
        self._animation = QPropertyAnimation(self._effect, b"blurRadius", self._button)
        self._animation.setDuration(180)
        self._animation.setStartValue(self._effect.blurRadius())
        self._animation.setEndValue(target)
        self._animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animation.start()


def _walk_widgets(root: QWidget) -> list[QWidget]:
    items = [root]
    for child in root.findChildren(QWidget):
        items.append(child)
    return items


def install_interactive_effects(root: QWidget) -> None:
    """Attach subtle hover glow to buttons and polish tables/inputs."""
    for widget in _walk_widgets(root):
        if isinstance(widget, QAbstractButton):
            if widget.property("_hover_polished"):
                effect = widget.graphicsEffect()
                if isinstance(effect, QGraphicsDropShadowEffect):
                    effect.setColor(QColor(current_palette().primary))
                continue
            widget.setProperty("_hover_polished", True)
            _ButtonHoverEffect(widget)

        if isinstance(widget, QTableWidget):
            widget.setAlternatingRowColors(True)
            widget.setShowGrid(True)
