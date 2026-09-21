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
