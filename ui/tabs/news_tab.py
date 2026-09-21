from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLineEdit, QLabel
)
from PyQt6.QtCore import Qt
from modules.news import NewsFetcher
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

        refresh_btn = QPushButton("刷新热榜")
        refresh_btn.clicked.connect(self._refresh)
        layout.addWidget(refresh_btn)

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
        self._worker.result_ready.connect(self._on_summary_ready)
        self._worker.error_occurred.connect(lambda e: self._chat_display.setText(f"获取失败：{e}"))
        self._worker.start()

    def _fetch_and_summarize(self):
        items = self._fetcher.fetch_all()
        if not items:
            return "暂时无法获取热榜数据，请检查网络连接。"
        prompt = self._fetcher.format_for_ai(items)
        self._history.append({"role": "user", "content": prompt})
        reply = self._ai.chat(self._history)
        self._history.append({"role": "assistant", "content": reply})
        return reply

    def _on_summary_ready(self, text):
        self._chat_display.setText(text)

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
