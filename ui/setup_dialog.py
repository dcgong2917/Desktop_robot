from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QHBoxLayout
)


class SetupDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("初始配置")
        self.setFixedSize(400, 220)
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("欢迎使用桌宠！请填写以下配置："))
        layout.addWidget(QLabel("智谱 AI API Key（必填）："))
        self.zhipu_key_input = QLineEdit()
        self.zhipu_key_input.setPlaceholderText("从 open.bigmodel.cn 获取")
        layout.addWidget(self.zhipu_key_input)

        layout.addWidget(QLabel("Replicate API Key（换皮功能需要，可留空）："))
        self.replicate_key_input = QLineEdit()
        self.replicate_key_input.setPlaceholderText("从 replicate.com 获取")
        layout.addWidget(self.replicate_key_input)

        btn_row = QHBoxLayout()
        ok_btn = QPushButton("保存并启动")
        ok_btn.clicked.connect(self.accept)
        btn_row.addWidget(ok_btn)
        layout.addLayout(btn_row)
