from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox,
    QLabel, QLineEdit, QPushButton, QListWidget,
)


def build_bookmarks_tab(ui):
    """Build the Bookmarks tab and attach widgets to the ui instance."""
    tab = QWidget()
    layout = QVBoxLayout()
    layout.setContentsMargins(10, 12, 10, 10)
    layout.setSpacing(8)

    grp_save = QGroupBox("Save Bookmark")
    gs = QVBoxLayout()
    gs.setSpacing(6)
    save_row = QHBoxLayout()
    ui.bookmark_name_edit = QLineEdit()
    ui.bookmark_name_edit.setPlaceholderText("Bookmark name...")
    ui.save_bookmark_btn = QPushButton("Save Current")
    ui.save_bookmark_btn.setObjectName("btn_primary")
    save_row.addWidget(ui.bookmark_name_edit)
    save_row.addWidget(ui.save_bookmark_btn)
    gs.addLayout(save_row)
    grp_save.setLayout(gs)
    layout.addWidget(grp_save)

    grp_list = QGroupBox("Saved Bookmarks")
    gl = QVBoxLayout()
    gl.setSpacing(6)
    ui.bookmarks_list = QListWidget()
    gl.addWidget(ui.bookmarks_list)
    btn_row = QHBoxLayout()
    ui.apply_bookmark_btn = QPushButton("Apply")
    ui.apply_bookmark_btn.setObjectName("btn_primary")
    ui.delete_bookmark_btn = QPushButton("Delete")
    ui.delete_bookmark_btn.setObjectName("btn_danger")
    btn_row.addWidget(ui.apply_bookmark_btn)
    btn_row.addWidget(ui.delete_bookmark_btn)
    gl.addLayout(btn_row)
    grp_list.setLayout(gl)
    layout.addWidget(grp_list)

    layout.addStretch()
    tab.setLayout(layout)
    return tab
