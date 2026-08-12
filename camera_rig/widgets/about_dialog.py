import webbrowser
from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PySide6.QtCore import Qt

from camera_rig.constants import VERSION, AUTHOR, GITHUB_URL, PAYPAL_URL
from camera_rig.theme import dark_palette, QSS


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About Camera Rig Controller")
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setFixedWidth(320)
        self.setPalette(dark_palette())
        self.setStyleSheet(QSS)

        vbox = QVBoxLayout(self)
        vbox.setContentsMargins(24, 24, 24, 24)
        vbox.setSpacing(12)

        title = QLabel("CAMERA RIG CONTROLLER")
        title.setObjectName("lbl_header")
        title.setAlignment(Qt.AlignCenter)
        vbox.addWidget(title)

        ver = QLabel(f"Version {VERSION}")
        ver.setObjectName("lbl_sub")
        ver.setAlignment(Qt.AlignCenter)
        vbox.addWidget(ver)

        line = QLabel()
        line.setFixedHeight(1)
        line.setStyleSheet("background: #3a3a3a;")
        vbox.addWidget(line)

        author = QLabel(f"Developed by  <b>{AUTHOR}</b>")
        author.setStyleSheet("color: #aaa; font-size: 12px;")
        author.setAlignment(Qt.AlignCenter)
        vbox.addWidget(author)

        vbox.addSpacing(6)

        btn_gh = QPushButton("  View on GitHub")
        btn_gh.setFixedHeight(36)
        btn_gh.setCursor(Qt.PointingHandCursor)
        btn_gh.setStyleSheet(
            "QPushButton { background:#24292e; color:#fff; border:none;"
            " border-radius:4px; font-size:12px; font-weight:600; }"
            " QPushButton:hover { background:#3a4046; }"
            " QPushButton:pressed { background:#1a1e22; }"
        )
        btn_gh.clicked.connect(lambda: webbrowser.open(GITHUB_URL))
        vbox.addWidget(btn_gh)

        btn_pp = QPushButton("  Support via PayPal")
        btn_pp.setFixedHeight(36)
        btn_pp.setCursor(Qt.PointingHandCursor)
        btn_pp.setStyleSheet(
            "QPushButton { background:#009cde; color:#fff; border:none;"
            " border-radius:4px; font-size:12px; font-weight:600; }"
            " QPushButton:hover { background:#00b3ff; }"
            " QPushButton:pressed { background:#007ab0; }"
        )
        btn_pp.clicked.connect(lambda: webbrowser.open(PAYPAL_URL))
        vbox.addWidget(btn_pp)

        vbox.addSpacing(4)
        btn_close = QPushButton("Close")
        btn_close.setFixedHeight(30)
        btn_close.clicked.connect(self.accept)
        vbox.addWidget(btn_close)
