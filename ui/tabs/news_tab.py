from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QLabel, QComboBox
)
from modules.news import NewsFetcher, CATEGORIES
from services.zhipu_client import ZhipuClient
from workers.async_worker import AsyncWorker


class NewsTab(QWidget):
    def __init__(self, fetcher: NewsFetcher, ai_client: ZhipuClient):
        super().__init__()
        self._fetcher = fetcher
        self._ai = ai_client
        self._history = []
        self._worker = None

        layout = QVBoxLayout(self)

        top_row = QHBoxLayout()
        top_row.addWidget(QLabel("分类："))
        self._category_box = QComboBox()
        self._category_box.addItems(list(CATEGORIES.keys()))
        top_row.addWidget(self._category_box, stretch=1)
        refresh_btn = QPushButton("刷新热榜")
        refresh_btn.clicked.connect(self._refresh)
        top_row.addWidget(refresh_btn)
        layout.addLayout(top_row)

        self._chat_display = QTextEdit()
        self._chat_display.setReadOnly(True)
        layout.addWidget(self._chat_display)

        input_row = QHBoxLayout()
        self._input = QLineEdit()
        self._input.setPlaceholderText("追问热榜内容...")
        self._input.returnPressed.connect(self._send_question)
        send_btn = QPushButton("发送")
        send_btn.clicked.connect(self._send_question)
        input_row.addWidget(self._input)
        input_row.addWidget(send_btn)
        layout.addLayout(input_row)

    def _refresh(self):
        self._chat_display.setText("正在获取热榜...")
        self._history = []
        self._worker = AsyncWorker(self._fetch_and_summarize)
        self._worker.result_ready.connect(self._chat_display.setText)
        self._worker.error_occurred.connect(lambda e: self._chat_display.setText(f"获取失败：{e}"))
        self._worker.start()

    def _fetch_and_summarize(self):
        category = self._category_box.currentText()
        items, err = self._fetcher.fetch_category(category)
        if not items:
            return f"暂时无法获取热榜数据。\n\n详细错误：\n{err}"
        lines = [f"📰 {category} 热榜\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. {item['title']}")
        lines.append("\n💬 可以在下方追问任意内容")
        result = "\n".join(lines)
        self._history = [{"role": "user", "content": self._fetcher.format_for_ai(items)},
                         {"role": "assistant", "content": result}]
        return result

    def _send_question(self):
        question = self._input.text().strip()
        if not question or not self._history:
            return
        self._input.clear()
        self._history.append({"role": "user", "content": question})
        self._chat_display.append(f"\n你：{question}\n")
        self._chat_display.append("AI：")

        self._worker = AsyncWorker(self._ai.chat_stream, self._history, stream=True)
        self._worker.chunk_received.connect(self._append_chunk)
        self._worker.result_ready.connect(self._on_stream_done)
        self._worker.start()
        self._accumulated = ""

    def _append_chunk(self, chunk: str):
        self._accumulated += chunk
        cursor = self._chat_display.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        cursor.insertText(chunk)
        self._chat_display.setTextCursor(cursor)

    def _on_stream_done(self, _):
        self._history.append({"role": "assistant", "content": self._accumulated})
        self._accumulated = ""
