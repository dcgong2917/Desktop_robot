import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog, QScrollArea, QGridLayout, QFrame
)
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import QSize
from modules.skin import SkinGenerator
from workers.async_worker import AsyncWorker


class SkinTab(QWidget):
    skin_changed = None  # 外部设置为回调函数 fn(path)

    def __init__(self, generator: SkinGenerator, config, replicate_api_key: str = ""):
        super().__init__()
        self._gen = generator
        self._config = config
        self._has_key = bool(replicate_api_key)
        self._preview_path = None
        self._worker = None

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("方式一：上传参考图"))
        upload_btn = QPushButton("选择图片文件")
        upload_btn.clicked.connect(self._upload_image)
        layout.addWidget(upload_btn)

        layout.addWidget(QLabel("方式二：文字描述"))
        self._desc_input = QLineEdit()
        self._desc_input.setPlaceholderText("角色名或描述，如：雷电将军、蓝色猫耳少女")
        layout.addWidget(self._desc_input)
        gen_btn = QPushButton("AI 生成角色")
        gen_btn.clicked.connect(self._generate_from_text)
        layout.addWidget(gen_btn)

        self._status = QLabel("")
        layout.addWidget(self._status)

        preview_row = QHBoxLayout()
        self._preview = QLabel("预览将在此显示")
        self._preview.setFixedSize(100, 100)
        preview_row.addWidget(self._preview)
        self._apply_btn = QPushButton("应用为桌宠")
        self._apply_btn.setEnabled(False)
        self._apply_btn.clicked.connect(self._apply_skin)
        preview_row.addWidget(self._apply_btn)
        preview_row.addStretch()
        layout.addLayout(preview_row)

        layout.addWidget(QLabel("历史皮肤："))
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(130)
        self._history_widget = QWidget()
        self._history_layout = QGridLayout(self._history_widget)
        self._history_layout.setSpacing(6)
        scroll.setWidget(self._history_widget)
        layout.addWidget(scroll)

        current = self._config.get("current_skin")
        if current and os.path.exists(current):
            self._add_to_history(current)
        else:
            self._load_history()

    def _load_history(self):
        # 清空
        while self._history_layout.count():
            item = self._history_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        history = self._config.get("skin_history") or []
        for i, path in enumerate(reversed(history)):
            if not os.path.exists(path):
                continue
            btn = QPushButton()
            btn.setFixedSize(80, 80)
            btn.setIconSize(QSize(72, 72))
            btn.setIcon(QIcon(QPixmap(path).scaled(72, 72)))
            btn.setToolTip(os.path.basename(path))
            btn.clicked.connect(lambda _, p=path: self._apply_path(p))
            self._history_layout.addWidget(btn, 0, i)

    def _add_to_history(self, path: str):
        history = self._config.get("skin_history") or []
        if path not in history:
            history.append(path)
        self._config.set("skin_history", history)
        self._load_history()

    def _upload_image(self):
        if not self._has_key:
            self._status.setText("请先在配置中填写智谱 API Key")
            return
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片 (*.png *.jpg *.jpeg)")
        if path:
            self._status.setText("生成中...")
            self._worker = AsyncWorker(self._gen.generate_from_image, path)
            self._worker.result_ready.connect(self._on_generated)
            self._worker.error_occurred.connect(lambda e: self._status.setText(f"生成失败：{e}"))
            self._worker.start()

    def _generate_from_text(self):
        if not self._has_key:
            self._status.setText("请先在配置中填写智谱 API Key")
            return
        desc = self._desc_input.text().strip()
        if not desc:
            self._status.setText("请输入描述")
            return
        self._status.setText("生成中，请稍候...")
        self._worker = AsyncWorker(self._gen.generate_from_description, desc)
        self._worker.result_ready.connect(self._on_generated)
        self._worker.error_occurred.connect(lambda e: self._status.setText(f"生成失败：{e}"))
        self._worker.start()

    def _on_generated(self, path: str):
        self._preview_path = path
        self._preview.setPixmap(QPixmap(path).scaled(100, 100))
        self._apply_btn.setEnabled(True)
        self._status.setText("生成完成，点击'应用'确认")

    def _apply_skin(self):
        if self._preview_path:
            self._apply_path(self._preview_path)

    def _apply_path(self, path: str):
        if self.skin_changed:
            self.skin_changed(path)
        self._add_to_history(path)
        self._status.setText(f"已应用：{os.path.basename(path)}")
