"""AI Assistant tab — natural language camera rig control."""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QTextEdit, QComboBox, QStackedWidget,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeyEvent


class _InputBox(QTextEdit):
    """Multi-line input — Enter sends, Shift+Enter adds new line."""
    def __init__(self, send_callback, parent=None):
        super().__init__(parent)
        self._send = send_callback
        self.setPlaceholderText(
            "Type a command... (Enter = send, Shift+Enter = new line)"
        )
        self.setFixedHeight(60)
        self.setStyleSheet(
            "background:#111; color:#d4d4d4; font-size:11px;"
            " border:1px solid #3a3a3a; border-radius:3px; padding:4px;"
        )

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            if event.modifiers() & Qt.ShiftModifier:
                super().keyPressEvent(event)   # Shift+Enter → new line
            else:
                self._send()                   # Enter → send
        else:
            super().keyPressEvent(event)


def build_ai_tab(ui):
    """Build the AI Assistant tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    # ── Provider Settings ─────────────────────────────────────────────
    grp_settings = QGroupBox("Settings")
    gs = QVBoxLayout()
    gs.setSpacing(8)

    # Provider selector
    provider_row = QHBoxLayout()
    lbl_prov = QLabel("Provider:")
    lbl_prov.setObjectName("lbl_section")
    lbl_prov.setFixedWidth(70)
    ui.ai_provider_combo = QComboBox()
    ui.ai_provider_combo.addItems(["Claude API", "Local Model (Ollama / LM Studio)"])
    ui.ai_provider_combo.setCurrentIndex(1)  # default: Local Model
    provider_row.addWidget(lbl_prov)
    provider_row.addWidget(ui.ai_provider_combo)
    gs.addLayout(provider_row)

    # Stacked pages: one per provider
    ui.ai_settings_stack = QStackedWidget()

    # Page 0 — Claude API
    claude_page = QWidget()
    claude_layout = QVBoxLayout()
    claude_layout.setContentsMargins(0, 0, 0, 0)
    claude_layout.setSpacing(6)

    key_row = QHBoxLayout()
    lbl_key = QLabel("API Key:")
    lbl_key.setObjectName("lbl_section")
    lbl_key.setFixedWidth(70)
    ui.ai_api_key_edit = QLineEdit()
    ui.ai_api_key_edit.setEchoMode(QLineEdit.Password)
    ui.ai_api_key_edit.setPlaceholderText("sk-ant-api03-...")
    key_row.addWidget(lbl_key)
    key_row.addWidget(ui.ai_api_key_edit)
    claude_layout.addLayout(key_row)

    model_row = QHBoxLayout()
    lbl_model = QLabel("Model:")
    lbl_model.setObjectName("lbl_section")
    lbl_model.setFixedWidth(70)
    ui.ai_claude_model_combo = QComboBox()
    ui.ai_claude_model_combo.addItems([
        "claude-sonnet-4-5",
        "claude-haiku-4-5",
        "claude-opus-4-5",
    ])
    model_row.addWidget(lbl_model)
    model_row.addWidget(ui.ai_claude_model_combo)
    claude_layout.addLayout(model_row)

    claude_page.setLayout(claude_layout)
    ui.ai_settings_stack.addWidget(claude_page)

    # Page 1 — Local Model
    local_page = QWidget()
    local_layout = QVBoxLayout()
    local_layout.setContentsMargins(0, 0, 0, 0)
    local_layout.setSpacing(6)

    url_row = QHBoxLayout()
    lbl_url = QLabel("URL:")
    lbl_url.setObjectName("lbl_section")
    lbl_url.setFixedWidth(70)
    ui.ai_local_url_edit = QLineEdit()
    ui.ai_local_url_edit.setPlaceholderText("http://localhost:11434/v1")
    ui.ai_local_url_edit.setText("http://localhost:11434/v1")
    url_row.addWidget(lbl_url)
    url_row.addWidget(ui.ai_local_url_edit)
    local_layout.addLayout(url_row)

    lmodel_row = QHBoxLayout()
    lbl_lmodel = QLabel("Model:")
    lbl_lmodel.setObjectName("lbl_section")
    lbl_lmodel.setFixedWidth(70)
    ui.ai_local_model_edit = QLineEdit()
    ui.ai_local_model_edit.setPlaceholderText("llama3.1 / mistral / qwen2.5...")
    ui.ai_local_model_edit.setText("qwen3.5:9b")
    lmodel_row.addWidget(lbl_lmodel)
    lmodel_row.addWidget(ui.ai_local_model_edit)
    local_layout.addLayout(lmodel_row)

    local_page.setLayout(local_layout)
    ui.ai_settings_stack.addWidget(local_page)

    ui.ai_settings_stack.setCurrentIndex(1)  # default: Local Model page
    gs.addWidget(ui.ai_settings_stack)

    # Status label
    ui.ai_status_label = QLabel("Status: Not connected")
    ui.ai_status_label.setStyleSheet("color:#555; font-size:10px;")
    gs.addWidget(ui.ai_status_label)

    grp_settings.setLayout(gs)
    layout.addWidget(grp_settings)

    # ── Chat ──────────────────────────────────────────────────────────
    grp_chat = QGroupBox("AI Assistant")
    gc = QVBoxLayout()
    gc.setSpacing(6)

    ui.ai_chat_display = QTextEdit()
    ui.ai_chat_display.setReadOnly(True)
    ui.ai_chat_display.setMinimumHeight(220)
    ui.ai_chat_display.setStyleSheet(
        "background:#0d0d0d; color:#d4d4d4; font-size:11px;"
        " border:1px solid #3a3a3a; border-radius:3px;"
    )
    ui.ai_chat_display.setPlaceholderText(
        "Chat history will appear here...\n\n"
        "Examples:\n"
        "  'دوربین رو ۳۰ درجه به چپ بچرخون'\n"
        "  'Create a dolly shot from 0% to 100% in 120 frames'\n"
        "  'Set focal length to 85mm'"
    )
    gc.addWidget(ui.ai_chat_display)

    # Multi-line input — send callback wired in main_window after creation
    ui.ai_input_edit = _InputBox(send_callback=lambda: None)
    gc.addWidget(ui.ai_input_edit)

    send_row = QHBoxLayout()
    hint = QLabel("Enter=Send  ·  Shift+Enter=New line")
    hint.setStyleSheet("color:#444; font-size:9px;")
    send_row.addWidget(hint)
    send_row.addStretch()
    ui.ai_send_btn = QPushButton("Send")
    ui.ai_send_btn.setObjectName("btn_primary")
    ui.ai_send_btn.setFixedWidth(70)
    send_row.addWidget(ui.ai_send_btn)
    gc.addLayout(send_row)

    ui.ai_clear_btn = QPushButton("Clear Chat")
    ui.ai_clear_btn.setStyleSheet("font-size:10px;")
    gc.addWidget(ui.ai_clear_btn)

    grp_chat.setLayout(gc)
    layout.addWidget(grp_chat)

    layout.addStretch()
    tab.setLayout(layout)
    return tab
