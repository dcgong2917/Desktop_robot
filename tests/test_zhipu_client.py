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
