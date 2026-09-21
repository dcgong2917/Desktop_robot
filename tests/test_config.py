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
