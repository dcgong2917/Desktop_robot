import json
import urllib.request
from bs4 import BeautifulSoup

CATEGORIES = {
    "微博热搜": "_fetch_weibo",
    "百度热搜": "_fetch_baidu",
    "科技":     "_fetch_ithome",
    "财经":     "_fetch_sina_finance",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept-Language": "zh-CN,zh;q=0.9",
}


class NewsFetcher:
    def _get(self, url: str, extra_headers: dict = None) -> bytes:
        headers = {**HEADERS, **(extra_headers or {})}
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.read()

    def _fetch_weibo(self) -> tuple[list[dict], str]:
        try:
            data = json.loads(self._get(
                "https://weibo.com/ajax/side/hotSearch",
                {"Referer": "https://weibo.com/"}
            ))
            items = [
                {"source": "微博热搜", "title": i["word"]}
                for i in data["data"]["realtime"]
                if i.get("word") and not i.get("is_ad")
            ][:10]
            return items, ""
        except Exception as e:
            return [], str(e)

    def _fetch_baidu(self) -> tuple[list[dict], str]:
        try:
            html = self._get("https://top.baidu.com/board?tab=realtime")
            soup = BeautifulSoup(html, "html.parser")
            items = []
            for tag in soup.select(".c-single-text-ellipsis")[:10]:
                title = tag.get_text(strip=True)
                if title:
                    items.append({"source": "百度热搜", "title": title})
            return items, ""
        except Exception as e:
            return [], str(e)

    def _fetch_ithome(self) -> tuple[list[dict], str]:
        try:
            html = self._get("https://www.ithome.com/")
            soup = BeautifulSoup(html, "html.parser")
            items = []
            for tag in soup.select(".hot-list li a, #rank li a")[:10]:
                title = tag.get_text(strip=True)
                if title:
                    items.append({"source": "IT之家", "title": title})
            return items, ""
        except Exception as e:
            return [], str(e)

    def _fetch_sina_finance(self) -> tuple[list[dict], str]:
        try:
            html = self._get("https://finance.sina.com.cn/")
            soup = BeautifulSoup(html, "html.parser")
            items = []
            for tag in soup.select(".rank-list li a, .hot-list li a, .news-item a")[:10]:
                title = tag.get_text(strip=True)
                if title and len(title) > 5:
                    items.append({"source": "新浪财经", "title": title})
            if not items:
                # 备用：抓头条链接
                for tag in soup.find_all("a", href=True)[:60]:
                    title = tag.get_text(strip=True)
                    if len(title) > 10 and "财" in title or "股" in title or "经济" in title:
                        items.append({"source": "新浪财经", "title": title})
                    if len(items) >= 8:
                        break
            return items, ""
        except Exception as e:
            return [], str(e)

    def fetch_category(self, category: str) -> tuple[list[dict], str]:
        method_name = CATEGORIES.get(category)
        if not method_name:
            return [], f"未知分类：{category}"
        return getattr(self, method_name)()

    def format_for_ai(self, items: list[dict]) -> str:
        lines = ["以下是今日热榜内容，请用轻松有趣的方式总结 3-5 条最值得关注的内容：\n"]
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. [{item['source']}] {item['title']}")
        return "\n".join(lines)
