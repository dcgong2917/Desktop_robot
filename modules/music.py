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

    def get_qq_music_url(self, title: str, artist: str) -> str:
        query = urllib.parse.quote(f"{title} {artist}")
        return f"https://y.qq.com/n/ryqq/search?w={query}&t=song"
