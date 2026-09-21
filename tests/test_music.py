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
    import urllib.parse
    rec = MusicRecommender(client=MagicMock())
    url = rec.get_netease_url("晴天", "周杰伦")
    assert "music.163.com" in url
    assert "晴天" in urllib.parse.unquote(url)
