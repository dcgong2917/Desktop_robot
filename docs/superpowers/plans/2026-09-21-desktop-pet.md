# 桌宠机器人实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个 Windows 桌面宠物应用，提供剪贴板管理、热榜聚合对话、音乐推荐、换皮四大功能。

**Architecture:** 单进程 PyQt6 应用，透明无边框角色窗口常驻桌面，点击弹出 Tab 功能面板。所有网络/AI 调用通过 QThread 异步执行，智谱 AI API 提供对话和推荐能力。

**Tech Stack:** Python 3.11+, PyQt6, zhipuai SDK, httpx, pyperclip, replicate, PyInstaller

---

## 文件结构

```
robot/
├── main.py                        # 入口
├── ui/
│   ├── __init__.py
│   ├── pet_widget.py              # 角色窗口
│   ├── panel_widget.py            # 功能面板容器
│   ├── tabs/
│   │   ├── __init__.py
│   │   ├── clipboard_tab.py       # 剪贴板 Tab
│   │   ├── news_tab.py            # 热榜 Tab
│   │   ├── music_tab.py           # 音乐 Tab
│   │   └── skin_tab.py            # 换皮 Tab
│   └── setup_dialog.py            # 首次启动配置对话框
├── modules/
│   ├── __init__.py
│   ├── clipboard.py               # 剪贴板数据管理
│   ├── news.py                    # 热榜数据拉取
│   ├── music.py                   # 音乐推荐逻辑
│   └── skin.py                    # 换皮/图像生成
├── services/
│   ├── __init__.py
│   └── zhipu_client.py            # 智谱 AI API 封装
├── workers/
│   ├── __init__.py
│   └── async_worker.py            # QThread 通用异步工作线程
├── config.py                      # 配置读写
├── assets/
│   └── default_pet.gif            # 默认角色（需手动准备）
├── data/                          # 运行时数据目录（自动创建）
├── tests/
│   ├── test_clipboard.py
│   ├── test_config.py
│   ├── test_zhipu_client.py
│   ├── test_news.py
│   └── test_music.py
└── requirements.txt
```

---

## Task 1: 项目初始化

**Files:**
- Create: `requirements.txt`
- Create: `main.py`
- Create: `ui/__init__.py`
- Create: `modules/__init__.py`
- Create: `services/__init__.py`
- Create: `workers/__init__.py`
- Create: `ui/tabs/__init__.py`

- [ ] **Step 1: 创建 requirements.txt**

```
PyQt6>=6.6.0
zhipuai>=2.1.0
httpx>=0.27.0
replicate>=0.25.0
pyperclip>=1.8.2
pytest>=8.0.0
pytest-qt>=4.4.0
```

- [ ] **Step 2: 安装依赖**

```bash
pip install -r requirements.txt
```

预期：无报错，所有包安装成功。

- [ ] **Step 3: 创建空 __init__.py 文件**

```bash
mkdir -p ui/tabs modules services workers data tests
touch ui/__init__.py ui/tabs/__init__.py modules/__init__.py services/__init__.py workers/__init__.py
```

- [ ] **Step 4: 创建最小 main.py**

```python
import sys
from PyQt6.QtWidgets import QApplication


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    print("App started")
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 5: 验证 PyQt6 可运行**

```bash
python main.py
```

预期：打印 "App started"，进程挂起（Ctrl+C 退出）。

- [ ] **Step 6: Commit**

```bash
git init
git add .
git commit -m "chore: project scaffold"
```

---

## Task 2: 配置管理

**Files:**
- Create: `config.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_config.py
import json
import os
import pytest
from config import Config


def test_config_creates_default_file(tmp_path):
    cfg = Config(config_path=str(tmp_path / "config.json"))
    assert cfg.get("zhipu_api_key") == ""
    assert cfg.get("window_x") == 100
    assert cfg.get("window_y") == 100
    assert cfg.get("current_skin") == "assets/default_pet.gif"
    assert (tmp_path / "config.json").exists()


def test_config_saves_and_loads(tmp_path):
    path = str(tmp_path / "config.json")
    cfg = Config(config_path=path)
    cfg.set("zhipu_api_key", "test-key-123")
    cfg2 = Config(config_path=path)
    assert cfg2.get("zhipu_api_key") == "test-key-123"


def test_config_get_missing_key_returns_none(tmp_path):
    cfg = Config(config_path=str(tmp_path / "config.json"))
    assert cfg.get("nonexistent") is None
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_config.py -v
```

预期：FAIL，`ModuleNotFoundError: No module named 'config'`

- [ ] **Step 3: 实现 config.py**

```python
import json
import os

_DEFAULTS = {
    "zhipu_api_key": "",
    "replicate_api_key": "",
    "window_x": 100,
    "window_y": 100,
    "current_skin": "assets/default_pet.gif",
}


class Config:
    def __init__(self, config_path="data/config.json"):
        self._path = config_path
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
        else:
            self._data = dict(_DEFAULTS)
            self._save()

    def get(self, key):
        return self._data.get(key)

    def set(self, key, value):
        self._data[key] = value
        self._save()

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: 运行确认通过**

```bash
pytest tests/test_config.py -v
```

预期：3 passed

- [ ] **Step 5: Commit**

```bash
git add config.py tests/test_config.py
git commit -m "feat: add Config class with JSON persistence"
```

---

## Task 3: 智谱 AI 客户端

**Files:**
- Create: `services/zhipu_client.py`
- Create: `tests/test_zhipu_client.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_zhipu_client.py
from unittest.mock import MagicMock, patch
from services.zhipu_client import ZhipuClient


def test_chat_returns_string():
    client = ZhipuClient(api_key="fake-key")
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "Hello!"
    with patch.object(client._client.chat.completions, "create", return_value=mock_response):
        result = client.chat([{"role": "user", "content": "hi"}])
    assert result == "Hello!"


def test_chat_stream_yields_chunks():
    client = ZhipuClient(api_key="fake-key")

    def mock_stream():
        for text in ["Hello", " World"]:
            chunk = MagicMock()
            chunk.choices = [MagicMock()]
            chunk.choices[0].delta.content = text
            yield chunk

    with patch.object(client._client.chat.completions, "create", return_value=mock_stream()):
        chunks = list(client.chat_stream([{"role": "user", "content": "hi"}]))
    assert chunks == ["Hello", " World"]
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_zhipu_client.py -v
```

预期：FAIL，`ModuleNotFoundError`

- [ ] **Step 3: 实现 services/zhipu_client.py**

```python
from zhipuai import ZhipuAI


class ZhipuClient:
    MODEL = "glm-4-flash"

    def __init__(self, api_key: str):
        self._client = ZhipuAI(api_key=api_key)

    def chat(self, messages: list[dict]) -> str:
        response = self._client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
        )
        return response.choices[0].message.content

    def chat_stream(self, messages: list[dict]):
        response = self._client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
```

- [ ] **Step 4: 运行确认通过**

```bash
pytest tests/test_zhipu_client.py -v
```

预期：2 passed

- [ ] **Step 5: Commit**

```bash
git add services/zhipu_client.py tests/test_zhipu_client.py
git commit -m "feat: add ZhipuClient with chat and stream support"
```

---

## Task 4: 通用异步工作线程

**Files:**
- Create: `workers/async_worker.py`

- [ ] **Step 1: 实现 workers/async_worker.py**

这个类把任意函数包装成 QThread，完成后通过信号通知 UI 线程，无需为每个 API 调用写独立 QThread 子类。

```python
from PyQt6.QtCore import QThread, pyqtSignal


class AsyncWorker(QThread):
    result_ready = pyqtSignal(object)
    error_occurred = pyqtSignal(str)
    chunk_received = pyqtSignal(str)  # 流式回复用

    def __init__(self, fn, *args, stream=False, **kwargs):
        super().__init__()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self._stream = stream

    def run(self):
        try:
            if self._stream:
                for chunk in self._fn(*self._args, **self._kwargs):
                    self.chunk_received.emit(chunk)
                self.result_ready.emit(None)
            else:
                result = self._fn(*self._args, **self._kwargs)
                self.result_ready.emit(result)
        except Exception as e:
            self.error_occurred.emit(str(e))
```

- [ ] **Step 2: Commit**

```bash
git add workers/async_worker.py
git commit -m "feat: add AsyncWorker QThread wrapper"
```

---

## Task 5: 剪贴板模块

**Files:**
- Create: `modules/clipboard.py`
- Create: `tests/test_clipboard.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_clipboard.py
import pytest
from modules.clipboard import ClipboardManager


def test_add_and_list(tmp_path):
    mgr = ClipboardManager(data_path=str(tmp_path / "clips.json"))
    mgr.add("SSH 登录", "ssh user@192.168.1.100")
    items = mgr.list()
    assert len(items) == 1
    assert items[0]["name"] == "SSH 登录"
    assert items[0]["content"] == "ssh user@192.168.1.100"
    assert "id" in items[0]
    assert "created_at" in items[0]


def test_delete(tmp_path):
    mgr = ClipboardManager(data_path=str(tmp_path / "clips.json"))
    mgr.add("A", "aaa")
    item_id = mgr.list()[0]["id"]
    mgr.delete(item_id)
    assert mgr.list() == []


def test_update(tmp_path):
    mgr = ClipboardManager(data_path=str(tmp_path / "clips.json"))
    mgr.add("Old Name", "old content")
    item_id = mgr.list()[0]["id"]
    mgr.update(item_id, name="New Name", content="new content")
    item = mgr.list()[0]
    assert item["name"] == "New Name"
    assert item["content"] == "new content"


def test_persistence(tmp_path):
    path = str(tmp_path / "clips.json")
    mgr = ClipboardManager(data_path=path)
    mgr.add("Test", "content")
    mgr2 = ClipboardManager(data_path=path)
    assert len(mgr2.list()) == 1
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_clipboard.py -v
```

预期：4 FAILED

- [ ] **Step 3: 实现 modules/clipboard.py**

```python
import json
import os
import uuid
from datetime import datetime


class ClipboardManager:
    def __init__(self, data_path="data/clips.json"):
        self._path = data_path
        os.makedirs(os.path.dirname(self._path) or ".", exist_ok=True)
        self._items = []
        if os.path.exists(self._path):
            with open(self._path, "r", encoding="utf-8") as f:
                self._items = json.load(f)

    def list(self) -> list[dict]:
        return list(self._items)

    def add(self, name: str, content: str):
        item = {
            "id": str(uuid.uuid4()),
            "name": name,
            "content": content,
            "created_at": datetime.now().isoformat(),
        }
        self._items.append(item)
        self._save()

    def delete(self, item_id: str):
        self._items = [i for i in self._items if i["id"] != item_id]
        self._save()

    def update(self, item_id: str, name: str = None, content: str = None):
        for item in self._items:
            if item["id"] == item_id:
                if name is not None:
                    item["name"] = name
                if content is not None:
                    item["content"] = content
                break
        self._save()

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._items, f, ensure_ascii=False, indent=2)
```

- [ ] **Step 4: 运行确认通过**

```bash
pytest tests/test_clipboard.py -v
```

预期：4 passed

- [ ] **Step 5: Commit**

```bash
git add modules/clipboard.py tests/test_clipboard.py
git commit -m "feat: add ClipboardManager with CRUD and persistence"
```

---

## Task 6: 热榜数据拉取模块

**Files:**
- Create: `modules/news.py`
- Create: `tests/test_news.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_news.py
from unittest.mock import patch, MagicMock
from modules.news import NewsFetcher


def test_fetch_weibo_returns_list():
    fetcher = NewsFetcher()
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {
            "realtime": [
                {"note": "热点事件1", "num": 1000000},
                {"note": "热点事件2", "num": 800000},
            ]
        }
    }
    with patch("httpx.get", return_value=mock_response):
        items = fetcher.fetch_weibo()
    assert isinstance(items, list)
    assert len(items) == 2
    assert items[0]["title"] == "热点事件1"
    assert items[0]["source"] == "微博"


def test_fetch_returns_empty_on_error():
    fetcher = NewsFetcher()
    with patch("httpx.get", side_effect=Exception("network error")):
        items = fetcher.fetch_weibo()
    assert items == []


def test_format_for_ai():
    fetcher = NewsFetcher()
    items = [
        {"source": "微博", "title": "事件A"},
        {"source": "知乎", "title": "问题B"},
    ]
    text = fetcher.format_for_ai(items)
    assert "微博" in text
    assert "事件A" in text
    assert "知乎" in text
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_news.py -v
```

预期：3 FAILED

- [ ] **Step 3: 实现 modules/news.py**

```python
import httpx


class NewsFetcher:
    WEIBO_URL = "https://weibo.com/ajax/side/hotSearch"
    ZHIHU_URL = "https://www.zhihu.com/api/v3/feed/topstory/hot-lists/total?limit=10"

    def fetch_weibo(self) -> list[dict]:
        try:
            r = httpx.get(self.WEIBO_URL, timeout=10)
            r.raise_for_status()
            items = r.json()["data"]["realtime"]
            return [{"source": "微博", "title": i["note"]} for i in items[:10]]
        except Exception:
            return []

    def fetch_zhihu(self) -> list[dict]:
        try:
            headers = {"User-Agent": "Mozilla/5.0"}
            r = httpx.get(self.ZHIHU_URL, headers=headers, timeout=10)
            r.raise_for_status()
            items = r.json()["data"]
            return [{"source": "知乎", "title": i["target"]["title"]} for i in items[:10]]
        except Exception:
            return []

    def fetch_all(self) -> list[dict]:
        results = []
        results.extend(self.fetch_weibo())
        results.extend(self.fetch_zhihu())
        return results

    def format_for_ai(self, items: list[dict]) -> str:
        lines = ["以下是今日热榜内容，请用轻松有趣的方式总结 3-5 条最值得关注的内容：\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. [{item['source']}] {item['title']}")
        return "\n".join(lines)
```

- [ ] **Step 4: 运行确认通过**

```bash
pytest tests/test_news.py -v
```

预期：3 passed

- [ ] **Step 5: Commit**

```bash
git add modules/news.py tests/test_news.py
git commit -m "feat: add NewsFetcher for weibo and zhihu hot lists"
```

---

## Task 7: 音乐推荐模块

**Files:**
- Create: `modules/music.py`
- Create: `tests/test_music.py`

- [ ] **Step 1: 写失败测试**

```python
# tests/test_music.py
from unittest.mock import MagicMock
from modules.music import MusicRecommender


def test_build_prompt_with_mood():
    rec = MusicRecommender(client=MagicMock())
    prompt = rec.build_prompt("疲惫，想放松")
    assert "疲惫" in prompt
    assert "3-5 首" in prompt


def test_build_prompt_empty_mood():
    rec = MusicRecommender(client=MagicMock())
    prompt = rec.build_prompt("")
    assert "随机" in prompt or "自由" in prompt


def test_parse_recommendations():
    rec = MusicRecommender(client=MagicMock())
    ai_text = """1. 《晴天》- 周杰伦：轻快旋律让人心情舒畅
2. 《夜曲》- 周杰伦：钢琴声令人沉静
3. 《七里香》- 周杰伦：清新自然的感觉"""
    results = rec.parse_recommendations(ai_text)
    assert len(results) == 3
    assert results[0]["title"] == "晴天"
    assert results[0]["artist"] == "周杰伦"
    assert "轻快" in results[0]["reason"]


def test_get_netease_url():
    rec = MusicRecommender(client=MagicMock())
    url = rec.get_netease_url("晴天", "周杰伦")
    assert "music.163.com" in url
    assert "晴天" in url
```

- [ ] **Step 2: 运行确认失败**

```bash
pytest tests/test_music.py -v
```

预期：4 FAILED

- [ ] **Step 3: 实现 modules/music.py**

```python
import re
import urllib.parse


class MusicRecommender:
    def __init__(self, client):
        self._client = client

    def build_prompt(self, mood: str) -> str:
        if mood.strip():
            return f"我现在的心情/场景是：{mood}。请推荐 3-5 首适合的音乐，格式为：序号. 《歌名》- 歌手：一句推荐理由"
        return "请随机推荐 3-5 首好听的音乐，格式为：序号. 《歌名》- 歌手：一句推荐理由"

    def recommend(self, mood: str) -> str:
        prompt = self.build_prompt(mood)
        return self._client.chat([{"role": "user", "content": prompt}])

    def parse_recommendations(self, ai_text: str) -> list[dict]:
        results = []
        pattern = r"\d+\.\s*[《「](.+?)[》」]\s*[-—]\s*(.+?)：(.+)"
        for match in re.finditer(pattern, ai_text):
            results.append({
                "title": match.group(1).strip(),
                "artist": match.group(2).strip(),
                "reason": match.group(3).strip(),
            })
        return results

    def get_netease_url(self, title: str, artist: str) -> str:
        query = urllib.parse.quote(f"{title} {artist}")
        return f"https://music.163.com/#/search/m/?s={query}&type=1"
```

- [ ] **Step 4: 运行确认通过**

```bash
pytest tests/test_music.py -v
```

预期：4 passed

- [ ] **Step 5: Commit**

```bash
git add modules/music.py tests/test_music.py
git commit -m "feat: add MusicRecommender with netease URL generation"
```

---

## Task 8: 换皮模块

**Files:**
- Create: `modules/skin.py`

- [ ] **Step 1: 实现 modules/skin.py**

```python
import os
import httpx
import replicate


class SkinGenerator:
    def __init__(self, replicate_api_key: str, assets_dir: str = "assets"):
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
        self._assets_dir = assets_dir
        os.makedirs(assets_dir, exist_ok=True)

    def generate_from_description(self, description: str) -> str:
        """
        根据文字描述生成角色图，返回保存后的本地路径。
        """
        prompt = f"cute desktop pet character, {description}, transparent background, chibi style, high quality PNG"
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "negative_prompt": "background, shadow, blurry",
                "width": 512,
                "height": 512,
            },
        )
        image_url = output[0]
        return self._download_image(image_url, "custom_pet.png")

    def generate_from_image(self, image_path: str) -> str:
        """
        根据参考图生成风格类似的角色图，返回保存后的本地路径。
        """
        with open(image_path, "rb") as f:
            output = replicate.run(
                "tencentarc/photomaker-style:467d062309da518648ba89d226490e02b8ed09b5abc15026e54e31c5a8cd0769",
                input={
                    "input_image": f,
                    "prompt": "cute chibi desktop pet character img, transparent background",
                    "style_name": "Anime",
                    "num_outputs": 1,
                },
            )
        image_url = output[0]
        return self._download_image(image_url, "custom_pet.png")

    def _download_image(self, url: str, filename: str) -> str:
        response = httpx.get(url, timeout=60)
        response.raise_for_status()
        save_path = os.path.join(self._assets_dir, filename)
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path
```

- [ ] **Step 2: Commit**

```bash
git add modules/skin.py
git commit -m "feat: add SkinGenerator using Replicate API"
```

---

## Task 9: 角色窗口 UI

**Files:**
- Create: `ui/pet_widget.py`

- [ ] **Step 1: 实现 ui/pet_widget.py**

```python
import os
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QMovie, QPixmap
from PyQt6.QtWidgets import QLabel, QWidget, QMenu
from config import Config


class PetWidget(QWidget):
    def __init__(self, config: Config):
        super().__init__()
        self._config = config
        self._panel = None
        self._drag_pos = QPoint()
        self._setup_window()
        self._load_skin(config.get("current_skin"))

    def _setup_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(120, 120)
        x = self._config.get("window_x") or 100
        y = self._config.get("window_y") or 100
        self.move(x, y)

        self._label = QLabel(self)
        self._label.resize(120, 120)

    def _load_skin(self, path: str):
        if not path or not os.path.exists(path):
            path = "assets/default_pet.gif"
        if path.lower().endswith(".gif"):
            self._movie = QMovie(path)
            self._label.setMovie(self._movie)
            self._movie.start()
        else:
            pixmap = QPixmap(path).scaled(120, 120, Qt.AspectRatioMode.KeepAspectRatio)
            self._label.setPixmap(pixmap)

    def set_panel(self, panel):
        self._panel = panel

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            pos = self.pos()
            self._config.set("window_x", pos.x())
            self._config.set("window_y", pos.y())
            # 判断是点击还是拖拽（移动距离 < 5px 视为点击）
            moved = (event.globalPosition().toPoint() - self._drag_pos - self.pos()).manhattanLength()
            if moved < 5 and self._panel:
                self._toggle_panel()

    def _toggle_panel(self):
        if self._panel.isVisible():
            self._panel.hide()
        else:
            pet_pos = self.pos()
            self._panel.move(pet_pos.x() + 130, pet_pos.y())
            self._panel.show()
            self._panel.raise_()

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        quit_action = menu.addAction("退出")
        quit_action.triggered.connect(self._quit)
        menu.exec(pos)

    def _quit(self):
        from PyQt6.QtWidgets import QApplication
        QApplication.quit()

    def reload_skin(self, path: str):
        self._config.set("current_skin", path)
        self._load_skin(path)
```

- [ ] **Step 2: Commit**

```bash
git add ui/pet_widget.py
git commit -m "feat: add PetWidget with drag, click-to-toggle, skin loading"
```

---

## Task 10: 剪贴板 Tab UI

**Files:**
- Create: `ui/tabs/clipboard_tab.py`

- [ ] **Step 1: 实现 ui/tabs/clipboard_tab.py**

```python
import pyperclip
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QListWidgetItem, QDialog, QLineEdit,
    QLabel, QTextEdit, QMenu, QMessageBox
)
from PyQt6.QtCore import Qt
from modules.clipboard import ClipboardManager


class AddEditDialog(QDialog):
    def __init__(self, parent=None, name="", content=""):
        super().__init__(parent)
        self.setWindowTitle("添加/编辑")
        self.setFixedSize(320, 200)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("名称"))
        self.name_input = QLineEdit(name)
        layout.addWidget(self.name_input)
        layout.addWidget(QLabel("内容"))
        self.content_input = QTextEdit(content)
        self.content_input.setFixedHeight(80)
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
            preview = item["content"][:40] + ("..." if len(item["content"]) > 40 else "")
            list_item = QListWidgetItem(f"{item['name']}\n{preview}")
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
            name = dlg.name_input.text().strip()
            content = dlg.content_input.toPlainText().strip()
            if name and content:
                self._mgr.add(name, content)
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
                dlg = AddEditDialog(self, item["name"], item["content"])
                if dlg.exec():
                    self._mgr.update(item_id, dlg.name_input.text(), dlg.content_input.toPlainText())
                    self._refresh_list()
                break

    def _delete_item(self, item_id):
        self._mgr.delete(item_id)
        self._refresh_list()
```

- [ ] **Step 2: Commit**

```bash
git add ui/tabs/clipboard_tab.py
git commit -m "feat: add ClipboardTab with copy/add/edit/delete"
```

---

## Task 11: 热榜 Tab UI

**Files:**
- Create: `ui/tabs/news_tab.py`

- [ ] **Step 1: 实现 ui/tabs/news_tab.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add ui/tabs/news_tab.py
git commit -m "feat: add NewsTab with hot list summary and follow-up chat"
```

---

## Task 12: 音乐 Tab UI

**Files:**
- Create: `ui/tabs/music_tab.py`

- [ ] **Step 1: 实现 ui/tabs/music_tab.py**

```python
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
        url = self._rec.get_netease_url(song["title"], song["artist"])
        btn.clicked.connect(lambda _, u=url: webbrowser.open(u))
        row.addWidget(btn)
        self._result_layout.addWidget(frame)

    def _clear_results(self):
        while self._result_layout.count():
            item = self._result_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
```

- [ ] **Step 2: Commit**

```bash
git add ui/tabs/music_tab.py
git commit -m "feat: add MusicTab with AI recommendations and netease links"
```

---

## Task 13: 换皮 Tab UI

**Files:**
- Create: `ui/tabs/skin_tab.py`

- [ ] **Step 1: 实现 ui/tabs/skin_tab.py**

```python
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

    def __init__(self, generator: SkinGenerator):
        super().__init__()
        self._gen = generator
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
        path, _ = QFileDialog.getOpenFileName(self, "选择图片", "", "图片 (*.png *.jpg *.jpeg)")
        if path:
            self._status.setText("生成中...")
            self._worker = AsyncWorker(self._gen.generate_from_image, path)
            self._worker.result_ready.connect(self._on_generated)
            self._worker.error_occurred.connect(lambda e: self._status.setText(f"生成失败：{e}"))
            self._worker.start()

    def _generate_from_text(self):
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
```

- [ ] **Step 2: Commit**

```bash
git add ui/tabs/skin_tab.py
git commit -m "feat: add SkinTab with image upload and text-to-pet generation"
```

---

## Task 14: 首次启动配置对话框

**Files:**
- Create: `ui/setup_dialog.py`

- [ ] **Step 1: 实现 ui/setup_dialog.py**

```python
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
```

- [ ] **Step 2: Commit**

```bash
git add ui/setup_dialog.py
git commit -m "feat: add SetupDialog for first-run API key configuration"
```

---

## Task 15: 功能面板容器

**Files:**
- Create: `ui/panel_widget.py`

- [ ] **Step 1: 实现 ui/panel_widget.py**

```python
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
        skin_tab = SkinTab(generator)
        tabs.addTab(skin_tab, "🎨 换皮")

        layout.addWidget(tabs)
        self._skin_tab = skin_tab

    def set_pet_widget(self, pet):
        self._skin_tab.skin_changed = pet.reload_skin
```

- [ ] **Step 2: Commit**

```bash
git add ui/panel_widget.py
git commit -m "feat: add PanelWidget assembling all four tabs"
```

---

## Task 16: 组装 main.py 并端到端测试

**Files:**
- Modify: `main.py`

- [ ] **Step 1: 更新 main.py**

```python
import sys
import os
from PyQt6.QtWidgets import QApplication
from config import Config
from ui.pet_widget import PetWidget
from ui.panel_widget import PanelWidget
from ui.setup_dialog import SetupDialog


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = Config()

    # 首次启动检测
    if not config.get("zhipu_api_key"):
        dlg = SetupDialog()
        if dlg.exec():
            config.set("zhipu_api_key", dlg.zhipu_key_input.text().strip())
            config.set("replicate_api_key", dlg.replicate_key_input.text().strip())
        else:
            sys.exit(0)

    pet = PetWidget(config)
    panel = PanelWidget(config)
    panel.set_pet_widget(pet)
    pet.set_panel(panel)

    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: 运行所有测试**

```bash
pytest tests/ -v
```

预期：所有测试通过。

- [ ] **Step 3: 启动应用测试**

你需要先准备一张 GIF 图放到 `assets/default_pet.gif`（任意小动图即可，建议 120×120 像素）。

```bash
python main.py
```

预期：弹出配置对话框，填入智谱 API Key 后，桌面右上角出现宠物角色，点击后弹出功能面板。

- [ ] **Step 4: Commit**

```bash
git add main.py
git commit -m "feat: wire up main entry with setup dialog and pet+panel"
```

---

## Task 17: 打包为 Windows exe

**Files:**
- Create: `build.bat`

- [ ] **Step 1: 安装 PyInstaller**

```bash
pip install pyinstaller
```

- [ ] **Step 2: 创建 build.bat**

```bat
pyinstaller ^
  --onefile ^
  --windowed ^
  --name robot ^
  --add-data "assets;assets" ^
  main.py
```

- [ ] **Step 3: 执行打包（在 Windows 环境中运行）**

```bash
build.bat
```

预期：`dist/robot.exe` 生成，双击可直接运行。

- [ ] **Step 4: Commit**

```bash
git add build.bat
git commit -m "chore: add PyInstaller build script"
```

---

## 全部测试命令汇总

```bash
pytest tests/ -v
```

预期 pass 列表：
- `tests/test_config.py` — 3 tests
- `tests/test_clipboard.py` — 4 tests
- `tests/test_zhipu_client.py` — 2 tests
- `tests/test_news.py` — 3 tests
- `tests/test_music.py` — 4 tests

合计：16 tests
