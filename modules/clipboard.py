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

    def add(self, content: str):
        item = {
            "id": str(uuid.uuid4()),
            "content": content,
            "created_at": datetime.now().isoformat(),
        }
        self._items.append(item)
        self._save()

    def delete(self, item_id: str):
        self._items = [i for i in self._items if i["id"] != item_id]
        self._save()

    def update(self, item_id: str, content: str = None):
        for item in self._items:
            if item["id"] == item_id:
                if content is not None:
                    item["content"] = content
                break
        self._save()

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._items, f, ensure_ascii=False, indent=2)
