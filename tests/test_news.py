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
