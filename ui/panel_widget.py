from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTabWidget
from PyQt6.QtCore import Qt
from ui.tabs.clipboard_tab import ClipboardTab
from ui.tabs.news_tab import NewsTab
from ui.tabs.music_tab import MusicTab
from ui.tabs.skin_tab import SkinTab
from modules.clipboard import ClipboardManager
from modules.news import NewsFetcher
from modules.music import MusicRecommender
from modules.skin import SkinGenerator
from services.zhipu_client import ZhipuClient
from config import Config


class PanelWidget(QWidget):
    def __init__(self, config: Config):
        super().__init__()
        self._config = config
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setFixedSize(380, 480)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        tabs = QTabWidget()

        clipboard_mgr = ClipboardManager()
        tabs.addTab(ClipboardTab(clipboard_mgr), "📋 剪贴板")

        ai_client = ZhipuClient(api_key=config.get("zhipu_api_key"))
        fetcher = NewsFetcher()
        tabs.addTab(NewsTab(fetcher, ai_client), "🔥 热榜")

        recommender = MusicRecommender(ai_client)
        tabs.addTab(MusicTab(recommender), "🎵 音乐")

        replicate_key = config.get("replicate_api_key") or ""
        generator = SkinGenerator(replicate_api_key=replicate_key)
        skin_tab_widget = SkinTab(generator, replicate_api_key=replicate_key)
        tabs.addTab(skin_tab_widget, "🎨 换皮")

        layout.addWidget(tabs)
        self._skin_tab = skin_tab_widget

    def set_pet_widget(self, pet):
        self._skin_tab.skin_changed = pet.reload_skin
