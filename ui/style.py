STYLESHEET = """
/* ── 全局 ── */
QWidget {
    background-color: #1e1f2e;
    color: #e0e0f0;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 13px;
}

/* ── 面板主体 ── */
QTabWidget::pane {
    border: none;
    background: #1e1f2e;
}

QTabBar::tab {
    background: #2a2b3d;
    color: #9090b0;
    padding: 7px 14px;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 12px;
}
QTabBar::tab:selected {
    color: #a0b4ff;
    border-bottom: 2px solid #a0b4ff;
    background: #1e1f2e;
}
QTabBar::tab:hover:!selected {
    color: #c0c8f0;
    background: #252638;
}

/* ── 按钮 ── */
QPushButton {
    background-color: #3a3b55;
    color: #d0d8ff;
    border: none;
    border-radius: 8px;
    padding: 7px 16px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #4a4b70;
}
QPushButton:pressed {
    background-color: #5a5b85;
}
QPushButton:disabled {
    background-color: #2a2b3d;
    color: #555570;
}

/* ── 输入框 ── */
QLineEdit, QTextEdit {
    background-color: #2a2b3d;
    color: #e0e0f0;
    border: 1px solid #3a3b55;
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: #5060c0;
}
QLineEdit:focus, QTextEdit:focus {
    border: 1px solid #7080e0;
}

/* ── 下拉框 ── */
QComboBox {
    background-color: #2a2b3d;
    color: #e0e0f0;
    border: 1px solid #3a3b55;
    border-radius: 8px;
    padding: 5px 10px;
}
QComboBox:hover {
    border: 1px solid #7080e0;
}
QComboBox::drop-down {
    border: none;
    width: 24px;
}
QComboBox QAbstractItemView {
    background-color: #2a2b3d;
    color: #e0e0f0;
    border: 1px solid #3a3b55;
    selection-background-color: #4a4b70;
    outline: none;
}

/* ── 列表 ── */
QListWidget {
    background-color: #2a2b3d;
    border: 1px solid #3a3b55;
    border-radius: 8px;
    padding: 4px;
    outline: none;
}
QListWidget::item {
    padding: 6px 8px;
    border-radius: 6px;
}
QListWidget::item:selected {
    background-color: #4a4b70;
    color: #ffffff;
}
QListWidget::item:hover:!selected {
    background-color: #333450;
}

/* ── 滚动条 ── */
QScrollBar:vertical {
    background: #1e1f2e;
    width: 6px;
    border-radius: 3px;
}
QScrollBar::handle:vertical {
    background: #4a4b70;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

QScrollBar:horizontal {
    background: #1e1f2e;
    height: 6px;
    border-radius: 3px;
}
QScrollBar::handle:horizontal {
    background: #4a4b70;
    border-radius: 3px;
    min-width: 20px;
}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ── 标签 ── */
QLabel {
    color: #b0b8d8;
    background: transparent;
}

/* ── Frame ── */
QFrame[frameShape="1"] {
    background-color: #252638;
    border: 1px solid #3a3b55;
    border-radius: 8px;
    padding: 4px;
}

/* ── 滚动区域 ── */
QScrollArea {
    border: 1px solid #3a3b55;
    border-radius: 8px;
    background: #252638;
}

/* ── 对话菜单 ── */
QMenu {
    background-color: #2a2b3d;
    color: #e0e0f0;
    border: 1px solid #3a3b55;
    border-radius: 8px;
    padding: 4px;
}
QMenu::item {
    padding: 6px 20px;
    border-radius: 6px;
}
QMenu::item:selected {
    background-color: #4a4b70;
}
QMenu::separator {
    height: 1px;
    background: #3a3b55;
    margin: 4px 8px;
}
"""
