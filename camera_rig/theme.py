from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette


def dark_palette() -> QPalette:
    p = QPalette()
    BG      = QColor("#1e1e1e")
    SURFACE = QColor("#2a2a2a")
    FG      = QColor("#d4d4d4")
    ACCENT  = QColor("#e8823c")
    DIS     = QColor("#555555")
    p.setColor(QPalette.Window,          SURFACE)
    p.setColor(QPalette.WindowText,      FG)
    p.setColor(QPalette.Base,            BG)
    p.setColor(QPalette.AlternateBase,   SURFACE)
    p.setColor(QPalette.ToolTipBase,     BG)
    p.setColor(QPalette.ToolTipText,     FG)
    p.setColor(QPalette.Text,            FG)
    p.setColor(QPalette.Button,          SURFACE)
    p.setColor(QPalette.ButtonText,      FG)
    p.setColor(QPalette.BrightText,      Qt.white)
    p.setColor(QPalette.Link,            ACCENT)
    p.setColor(QPalette.Highlight,       ACCENT)
    p.setColor(QPalette.HighlightedText, Qt.black)
    p.setColor(QPalette.Disabled, QPalette.Text,       DIS)
    p.setColor(QPalette.Disabled, QPalette.ButtonText, DIS)
    return p


QSS = """
* { font-family: "Segoe UI", sans-serif; font-size: 12px; }

QWidget { background: #1e1e1e; color: #d4d4d4; }

QTabWidget::pane {
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    background: #1e1e1e;
}
QTabBar::tab {
    background: #2a2a2a;
    border: 1px solid #3a3a3a;
    border-bottom: none;
    border-radius: 3px 3px 0 0;
    padding: 5px 14px;
    color: #888;
    font-size: 11px;
    letter-spacing: 0.5px;
}
QTabBar::tab:selected { background: #1e1e1e; color: #e8823c; border-bottom: 2px solid #e8823c; }
QTabBar::tab:hover    { color: #d4d4d4; }
QTabBar::tab:disabled { color: #444; }

QGroupBox {
    border: 1px solid #3a3a3a;
    border-radius: 4px;
    margin-top: 10px;
    padding: 8px 6px 6px 6px;
    color: #888;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 4px;
}

QLineEdit, QSpinBox, QDoubleSpinBox {
    background: #111;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    padding: 4px 6px;
    color: #d4d4d4;
    selection-background-color: #e8823c;
}
QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus { border-color: #e8823c; }

QPushButton {
    background: #2f2f2f;
    border: 1px solid #444;
    border-radius: 3px;
    padding: 5px 12px;
    color: #d4d4d4;
}
QPushButton:hover   { background: #3a3a3a; border-color: #e8823c; }
QPushButton:pressed { background: #1a1a1a; }
QPushButton:disabled { color: #555; border-color: #333; }

QPushButton#btn_primary {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
        stop:0 #e8823c, stop:1 #c0601e);
    border: none;
    color: #fff;
    font-size: 12px;
    font-weight: 600;
    border-radius: 4px;
    padding: 7px 0;
    letter-spacing: 0.5px;
}
QPushButton#btn_primary:hover   { background: #f0944e; }
QPushButton#btn_primary:pressed { background: #b05010; }
QPushButton#btn_primary:disabled { background: #3a3a3a; color: #666; }

QPushButton#btn_danger {
    background: #3a1e1e;
    border: 1px solid #6a2a2a;
    color: #e05050;
    border-radius: 3px;
    padding: 5px 12px;
}
QPushButton#btn_danger:hover { background: #501e1e; border-color: #e05050; }

QComboBox {
    background: #111;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    padding: 4px 6px;
    color: #d4d4d4;
}
QComboBox:focus { border-color: #e8823c; }
QComboBox::drop-down { border: none; width: 20px; }
QComboBox QAbstractItemView {
    background: #1e1e1e;
    border: 1px solid #3a3a3a;
    selection-background-color: #e8823c;
    color: #d4d4d4;
}

QSlider::groove:horizontal {
    height: 4px;
    background: #3a3a3a;
    border-radius: 2px;
}
QSlider::handle:horizontal {
    width: 12px; height: 12px;
    background: #e8823c;
    border-radius: 6px;
    margin: -4px 0;
}
QSlider::sub-page:horizontal {
    background: #e8823c;
    border-radius: 2px;
}
QSlider:disabled::handle:horizontal { background: #555; }
QSlider:disabled::sub-page:horizontal { background: #444; }

QCheckBox { spacing: 6px; color: #d4d4d4; }
QCheckBox::indicator {
    width: 14px; height: 14px;
    border: 1px solid #555;
    border-radius: 2px;
    background: #111;
}
QCheckBox::indicator:checked { background: #e8823c; border-color: #e8823c; }

QLabel#lbl_header { color: #e8823c; font-size: 15px; font-weight: 700; letter-spacing: 1px; }
QLabel#lbl_sub    { color: #555;    font-size: 10px; letter-spacing: 2px; }
QLabel#lbl_section { color: #888;   font-size: 11px; text-transform: uppercase; letter-spacing: 1px; }

QListWidget {
    background: #111;
    border: 1px solid #3a3a3a;
    border-radius: 3px;
    color: #d4d4d4;
}
QListWidget::item:selected { background: #e8823c; color: #fff; }
"""
