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
