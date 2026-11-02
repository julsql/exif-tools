# python
from __future__ import annotations

import re
from datetime import datetime, time
from typing import Optional, Sequence

from PyQt6.QtCore import QDate, QPoint, QRect, Qt
from PyQt6.QtGui import QAction, QColor, QIcon, QPainter, QPen, QPixmap
from PyQt6.QtWidgets import QCalendarWidget, QLineEdit

DATE_ONLY_FORMAT = "%Y-%m-%d"
PLACEHOLDER = "AAAA-MM-JJ [HH:MM:SS]"
MAX_DIGITS = 14
# Séparateur inséré AVANT le chiffre d'index donné
SEPARATORS = {4: "-", 6: "-", 8: " ", 10: ":", 12: ":"}


def parse_date(text: str, formats: Sequence[str]) -> Optional[datetime]:
    text = (text or "").strip()
    for fmt in formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def format_digits(digits: str) -> str:
    """'20240506143' -> '2024-05-06 14:3' (formatage progressif pendant la saisie)."""
    out = []
    for i, c in enumerate(digits[:MAX_DIGITS]):
        if i in SEPARATORS:
            out.append(SEPARATORS[i])
        out.append(c)
    return "".join(out)


def position_for_digit_count(formatted: str, count: int) -> int:
    """Position du curseur dans `formatted` juste après le `count`-ième chiffre."""
    if count == 0:
        return 0
    seen = 0
    for pos, c in enumerate(formatted):
        if c.isdigit():
            seen += 1
            if seen == count:
                return pos + 1
    return len(formatted)


def calendar_icon(color: str) -> QIcon:
    pm = QPixmap(32, 32)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    pen = QPen(QColor(color), 2.5)
    p.setPen(pen)
    p.drawRoundedRect(QRect(5, 7, 22, 20), 3, 3)
    p.drawLine(5, 13, 27, 13)
    p.drawLine(11, 4, 11, 9)
    p.drawLine(21, 4, 21, 9)
    p.setBrush(QColor(color))
    for x in (10, 16, 22):
        for y in (18, 23):
            p.drawEllipse(QPoint(x, y), 1, 1)
    p.end()
    return QIcon(pm)


def clock_icon(color: str) -> QIcon:
    pm = QPixmap(32, 32)
    pm.fill(Qt.GlobalColor.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setPen(QPen(QColor(color), 2.5))
    p.drawEllipse(QPoint(16, 16), 11, 11)
    p.drawLine(16, 16, 16, 9)
    p.drawLine(16, 16, 21, 19)
    p.end()
    return QIcon(pm)


class DateTimeField(QLineEdit):
    """Champ date au format AAAA-MM-JJ, heure optionnelle (HH:MM:SS).

    - formatage automatique pendant la saisie (on tape juste les chiffres)
    - collage d'un format accepté (EXIF, JJ/MM/AAAA…) normalisé en fin d'édition
    - icônes intégrées : calendrier et suppression
    """

    def __init__(self, display_format: str, accepted_formats: Sequence[str], parent=None):
        super().__init__(parent)
        self._display_format = display_format
        self._accepted_formats = list(accepted_formats)

        self.setPlaceholderText(PLACEHOLDER)
        self.textEdited.connect(self._auto_format)
        # Connecté avant MetadataPanel : la valeur est normalisée avant validation
        self.editingFinished.connect(self.normalize)
        self.textChanged.connect(self._sync_actions)

        self.calendar_action = QAction(self)
        self.calendar_action.setToolTip("Choisir dans le calendrier")
        self.calendar_action.triggered.connect(self._open_calendar)
        self.addAction(self.calendar_action, QLineEdit.ActionPosition.TrailingPosition)

        self.time_action = QAction(self)
        self.time_action.setToolTip("Ajouter / modifier l'heure")
        self.time_action.triggered.connect(self._edit_time)
        self.addAction(self.time_action, QLineEdit.ActionPosition.TrailingPosition)

        self.clear_action = QAction(self)
        self.clear_action.setToolTip("Supprimer la date")
        self.clear_action.triggered.connect(self._on_clear)
        self.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)

        self._calendar = QCalendarWidget(self)
        self._calendar.setWindowFlags(Qt.WindowType.Popup)
        self._calendar.setGridVisible(False)
        self._calendar.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self._calendar.clicked.connect(self._on_calendar_picked)

        self._sync_actions()

    # --- Icônes / style ---

    def set_icons(self, clear_icon: QIcon, icon_color: str) -> None:
        self.clear_action.setIcon(clear_icon)
        self.calendar_action.setIcon(calendar_icon(icon_color))
        self.time_action.setIcon(clock_icon(icon_color))

    def setReadOnly(self, readonly: bool) -> None:
        super().setReadOnly(readonly)
        self._sync_actions()

    def _sync_actions(self, *_args) -> None:
        editable = not self.isReadOnly()
        self.calendar_action.setVisible(editable)
        self.time_action.setVisible(editable)
        self.clear_action.setVisible(editable and bool(self.text()))

    # --- Valeur ---

    def parsed(self) -> Optional[datetime]:
        return parse_date(self.text(), self._accepted_formats)

    def format_value(self, dt: datetime) -> str:
        if dt.time() == time(0, 0, 0):
            return dt.strftime(DATE_ONLY_FORMAT)
        return dt.strftime(self._display_format)

    def normalize(self) -> None:
        """Met la valeur au format canonique si elle est reconnue (sinon laissée telle quelle)."""
        text = self.text().strip()
        if not text:
            if self.text():
                self.setText("")
            return
        dt = self.parsed()
        if dt is not None:
            formatted = self.format_value(dt)
            if formatted != self.text():
                self.setText(formatted)

    def _auto_format(self, text: str) -> None:
        cursor = self.cursorPosition()
        # Édition au milieu (ne pas décaler les chiffres) ou format JJ/MM/AAAA :
        # on laisse tel quel, normalize() s'en charge en fin d'édition
        if cursor != len(text) or "/" in text:
            return
        digits_before = len(re.sub(r"\D", "", text[:cursor]))
        formatted = format_digits(re.sub(r"\D", "", text))
        if formatted != text:
            self.setText(formatted)
            self.setCursorPosition(position_for_digit_count(formatted, digits_before))

    # --- Calendrier / suppression ---

    def _open_calendar(self) -> None:
        dt = self.parsed()
        self._calendar.setSelectedDate(
            QDate(dt.year, dt.month, dt.day) if dt else QDate.currentDate()
        )
        self._calendar.adjustSize()
        pos = self.mapToGlobal(QPoint(self.width() - self._calendar.width(), self.height()))
        self._calendar.move(pos)
        self._calendar.show()

    def _on_calendar_picked(self, qdate: QDate) -> None:
        self._calendar.hide()
        current = self.parsed()
        t = current.time() if current else time(0, 0, 0)
        self.setText(self.format_value(datetime.combine(qdate.toPyDate(), t)))
        self.editingFinished.emit()

    def _edit_time(self) -> None:
        """Ajoute 12:00:00 si pas d'heure, puis sélectionne l'heure : il suffit de taper les chiffres."""
        dt = self.parsed()
        if dt is None and self.text().strip():
            # Saisie non reconnue : on garde la date si elle est lisible, sinon on ne touche à rien
            dt = parse_date(self.text()[:10], [DATE_ONLY_FORMAT])
            if dt is None:
                return
        if dt is None:
            dt = datetime.now()
        if self.text().strip() == "" or dt.time() == time(0, 0, 0) or len(self.text()) <= 10:
            dt = dt.replace(hour=12, minute=0, second=0, microsecond=0)
        self.setText(dt.strftime(self._display_format))
        self.setFocus()
        self.setSelection(11, len(self.text()) - 11)

    def _on_clear(self) -> None:
        self.setText("")
        self.editingFinished.emit()
