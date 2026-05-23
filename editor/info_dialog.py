# python
from __future__ import annotations

from PyQt6.QtCore import Qt
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

        btns = QHBoxLayout()
        btns.addStretch(1)

        close_btn = QPushButton("Fermer")
        close_btn.clicked.connect(self.accept)
        btns.addWidget(close_btn)

        layout.addLayout(btns)
