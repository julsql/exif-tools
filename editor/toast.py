# python
from __future__ import annotations

from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer
from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QGraphicsOpacityEffect

from editor.shared_data import StyleData


class Toast(QWidget):
    def __init__(self, parent: QWidget, style: StyleData, message: str, duration_ms: int = 2000):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating, True)

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
        self._fade_in.start()
        QTimer.singleShot(duration_ms, self._fade_out.start)

    def _position_near_top(self, parent: QWidget) -> None:
        parent_rect = parent.geometry()
        self.adjustSize()
        w = self.width()
        h = self.height()
        x = parent_rect.x() + (parent_rect.width() - w) // 2
        y = parent_rect.y() + 20
        self.setGeometry(x, y, w, h)