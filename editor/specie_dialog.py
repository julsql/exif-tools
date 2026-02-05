# python
from __future__ import annotations

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QHBoxLayout, QPushButton


class SpecieDialog(QDialog):
    def __init__(self, parent, specie: str, url: str | None):
        super().__init__(parent)
        self.setWindowTitle("Espèce détectée")
        self.setModal(True)

        layout = QVBoxLayout(self)

        if url:
            msg = QLabel(
                f"L'espèce <b>{specie}</b> a été reconnue.<br/>"
                f"Cliquez sur le lien pour plus d'infos :"
            )
            msg.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(msg)

            link = QLabel(f'<a href="{url}">{url}</a>')
            link.setTextFormat(Qt.TextFormat.RichText)
            link.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
            link.setOpenExternalLinks(False)
            link.linkActivated.connect(lambda _: QDesktopServices.openUrl(QUrl(url)))
            layout.addWidget(link)
        else:
            msg = QLabel(f"L'espèce <b>{specie}</b> a été reconnue.")
            msg.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(msg)

        btns = QHBoxLayout()
        btns.addStretch(1)

        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Annuler")

        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)

        btns.addWidget(ok_btn)
        btns.addWidget(cancel_btn)

        layout.addLayout(btns)