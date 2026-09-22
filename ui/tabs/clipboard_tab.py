import pyperclip
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QDialog,
    QLabel, QTextEdit, QMenu
)
from PyQt6.QtCore import Qt
from modules.clipboard import ClipboardManager


class AddEditDialog(QDialog):
    def __init__(self, parent=None, content=""):
        super().__init__(parent)
        self.setWindowTitle("添加/编辑")
        self.setFixedSize(320, 150)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("内容"))
        self.content_input = QTextEdit(content)
        self.content_input.setFixedHeight(70)
        layout.addWidget(self.content_input)
        btn_row = QHBoxLayout()
        ok_btn = QPushButton("确定")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("取消")
        cancel_btn.clicked.connect(self.reject)
        btn_row.addWidget(ok_btn)
        btn_row.addWidget(cancel_btn)
        layout.addLayout(btn_row)


class ClipboardTab(QWidget):
    def __init__(self, clipboard_mgr: ClipboardManager):
        super().__init__()
        self._mgr = clipboard_mgr
        layout = QVBoxLayout(self)

        add_btn = QPushButton("+ 新增")
        add_btn.clicked.connect(self._add_item)
        layout.addWidget(add_btn)

        self._list = QListWidget()
        self._list.itemClicked.connect(self._copy_item)
        self._list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._list.customContextMenuRequested.connect(self._show_context_menu)
        layout.addWidget(self._list)

        self._status = QLabel("")
        layout.addWidget(self._status)

        self._refresh_list()

    def _refresh_list(self):
        self._list.clear()
        for item in self._mgr.list():
            preview = item["content"][:60] + ("..." if len(item["content"]) > 60 else "")
            list_item = QListWidgetItem(preview)
            list_item.setData(Qt.ItemDataRole.UserRole, item["id"])
            self._list.addItem(list_item)

    def _copy_item(self, list_item):
        item_id = list_item.data(Qt.ItemDataRole.UserRole)
        for item in self._mgr.list():
            if item["id"] == item_id:
                pyperclip.copy(item["content"])
                self._status.setText("已复制！")
                break

    def _add_item(self):
        dlg = AddEditDialog(self)
        if dlg.exec():
            content = dlg.content_input.toPlainText().strip()
            if content:
                self._mgr.add(content)
                self._refresh_list()

    def _show_context_menu(self, pos):
        item = self._list.itemAt(pos)
        if not item:
            return
        item_id = item.data(Qt.ItemDataRole.UserRole)
        menu = QMenu(self)
        edit_action = menu.addAction("编辑")
        del_action = menu.addAction("删除")
        action = menu.exec(self._list.mapToGlobal(pos))
        if action == edit_action:
            self._edit_item(item_id)
        elif action == del_action:
            self._delete_item(item_id)

    def _edit_item(self, item_id):
        for item in self._mgr.list():
            if item["id"] == item_id:
                dlg = AddEditDialog(self, item["content"])
                if dlg.exec():
                    self._mgr.update(item_id, content=dlg.content_input.toPlainText())
                    self._refresh_list()
                break

    def _delete_item(self, item_id):
        self._mgr.delete(item_id)
        self._refresh_list()
