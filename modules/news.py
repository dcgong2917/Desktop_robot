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
