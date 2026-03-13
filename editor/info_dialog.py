# python
from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton


class InfoDialog(QDialog):
    def __init__(self, parent, title: str, message: str):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)

        layout = QVBoxLayout(self)

        msg = QLabel(message)
        msg.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(msg)
