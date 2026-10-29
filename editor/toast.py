# python
from __future__ import annotations

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect

from editor.shared_data import StyleData


class Toast(QWidget):
    def __init__(self, parent: QWidget, style: StyleData, message: str, duration_ms: int = 2000):
        # Widget enfant superposé (et non fenêtre Tool) : sous Linux, une fenêtre
        # native capte les clics malgré WA_TransparentForMouseEvents et masque
        # les boutons situés dessous.
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)
        self.effect.setOpacity(0.0)

        self.setStyleSheet(
            f"""
            QWidget {{
                background: {style.BG_COLOR};
                border: 1px solid {style.BORDER_COLOR};
                border-radius: 8px;
            }}
            QLabel {{
                color: {style.FONT_COLOR};
                font-size: 14px;
            }}
            """
        )

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        self.label = QLabel(message)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        self._fade_in = QPropertyAnimation(self.effect, b"opacity", self)
        self._fade_in.setDuration(180)
        self._fade_in.setStartValue(0.0)
        self._fade_in.setEndValue(1.0)
        self._fade_in.setEasingCurve(QEasingCurve.Type.OutCubic)

        self._fade_out = QPropertyAnimation(self.effect, b"opacity", self)
        self._fade_out.setDuration(220)
        self._fade_out.setStartValue(1.0)
        self._fade_out.setEndValue(0.0)
        self._fade_out.setEasingCurve(QEasingCurve.Type.InCubic)
        self._fade_out.finished.connect(self.close)

        self.adjustSize()
        self._position_near_top(parent)

        self.show()
        self.raise_()
        self._fade_in.start()
        QTimer.singleShot(duration_ms, self._fade_out.start)

    def _position_near_top(self, parent: QWidget) -> None:
        self.adjustSize()
        w = self.width()
        h = self.height()
        # Coordonnées relatives au parent : pas de dépendance au gestionnaire
        # de fenêtres (X11, Wayland, macOS).
        x = (parent.width() - w) // 2
        y = 20
        self.setGeometry(x, y, w, h)