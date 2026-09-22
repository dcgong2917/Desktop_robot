import webbrowser
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLineEdit, QLabel, QScrollArea, QFrame
)
from modules.music import MusicRecommender
from workers.async_worker import AsyncWorker


class MusicTab(QWidget):
    def __init__(self, recommender: MusicRecommender):
        super().__init__()
        self._rec = recommender
        self._worker = None

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("心情或场景（可留空）："))

        self._mood_input = QLineEdit()
        self._mood_input.setPlaceholderText("例如：疲惫想放松，或者留空随机推荐")
        layout.addWidget(self._mood_input)

        recommend_btn = QPushButton("推荐音乐")
        recommend_btn.clicked.connect(self._recommend)
        layout.addWidget(recommend_btn)

        self._status = QLabel("")
        layout.addWidget(self._status)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self._result_container = QWidget()
        self._result_layout = QVBoxLayout(self._result_container)
        scroll.setWidget(self._result_container)
        layout.addWidget(scroll)

    def _recommend(self):
        mood = self._mood_input.text()
        self._status.setText("AI 推荐中...")
        self._clear_results()
        self._worker = AsyncWorker(self._rec.recommend, mood)
        self._worker.result_ready.connect(self._on_result)
        self._worker.error_occurred.connect(lambda e: self._status.setText(f"推荐失败：{e}"))
        self._worker.start()

    def _on_result(self, ai_text: str):
        self._status.setText("")
        songs = self._rec.parse_recommendations(ai_text)
        if not songs:
            self._status.setText("解析失败，原始结果：\n" + ai_text)
            return
        for song in songs:
            self._add_song_card(song)

    def _add_song_card(self, song: dict):
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        row = QHBoxLayout(frame)
        info = QLabel(f"<b>{song['title']}</b> - {song['artist']}<br><small>{song['reason']}</small>")
        info.setWordWrap(True)
        row.addWidget(info, stretch=1)
        btn = QPushButton("去听")
        url = self._rec.get_qq_music_url(song["title"], song["artist"])
        btn.clicked.connect(lambda _, u=url: webbrowser.open(u))
        row.addWidget(btn)
        self._result_layout.addWidget(frame)

    def _clear_results(self):
        while self._result_layout.count():
            item = self._result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
