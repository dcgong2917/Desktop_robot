import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QLabel, QFileDialog
)
from PyQt6.QtGui import QPixmap
from modules.skin import SkinGenerator
from workers.async_worker import AsyncWorker


class SkinTab(QWidget):
    skin_changed = None  # 外部设置为回调函数 fn(path)

    def __init__(self, generator: SkinGenerator, replicate_api_key: str = ""):
        super().__init__()
        self._gen = generator
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
        self._desc_input.setPlaceholderText("例如：蓝色猫耳少女，可爱风格")
        layout.addWidget(self._desc_input)
        gen_btn = QPushButton("AI 生成角色")
        gen_btn.clicked.connect(self._generate_from_text)
        layout.addWidget(gen_btn)

        self._status = QLabel("")
        layout.addWidget(self._status)

        self._preview = QLabel("预览将在此显示")
        self._preview.setFixedSize(120, 120)
        layout.addWidget(self._preview)

        self._apply_btn = QPushButton("应用为桌宠")
        self._apply_btn.setEnabled(False)
        self._apply_btn.clicked.connect(self._apply_skin)
        layout.addWidget(self._apply_btn)

    def _upload_image(self):
        if not self._has_key:
            self._status.setText("请先在配置中填写 Replicate API Key")
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
            self._status.setText("请先在配置中填写 Replicate API Key")
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
        pixmap = QPixmap(path).scaled(120, 120)
        self._preview.setPixmap(pixmap)
        self._apply_btn.setEnabled(True)
        self._status.setText("生成完成，点击'应用'确认")

    def _apply_skin(self):
        if self._preview_path and self.skin_changed:
            self.skin_changed(self._preview_path)
            self._status.setText("已应用！")
