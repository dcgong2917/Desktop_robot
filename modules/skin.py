import os
import base64
import httpx
from zhipuai import ZhipuAI
from rembg import remove, new_session


class SkinGenerator:
    def __init__(self, api_key: str, assets_dir: str = "assets"):
        self._client = ZhipuAI(api_key=api_key)
        self._assets_dir = assets_dir
        os.makedirs(assets_dir, exist_ok=True)
        self._rembg_session = new_session("u2netp")  # 轻量模型，~4MB

    def _unique_name(self, prefix: str) -> str:
        import time
        ts = int(time.time())
        return f"{prefix}_{ts}.png"

    def generate_from_description(self, description: str) -> str:
        prompt = f"{description}, chibi cute style, full body, simple white background, no text"
        response = self._client.images.generations(
            model="cogview-3-flash",
            prompt=prompt,
        )
        image_url = response.data[0].url
        raw_path = self._download_image(image_url, self._unique_name("raw"))
        return self._remove_background(raw_path, self._unique_name("pet"))

    def generate_from_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
        vision = self._client.chat.completions.create(
            model="glm-4v-flash",
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}},
                    {"type": "text", "text": "用英文简短描述这张图片里角色的外观特征（颜色、发型、服装等），50词以内"},
                ],
            }],
        )
        desc = vision.choices[0].message.content
        prompt = f"cute chibi desktop pet character, {desc}, simple clean design, white background, anime style"
        response = self._client.images.generations(
            model="cogview-3-flash",
            prompt=prompt,
        )
        image_url = response.data[0].url
        raw_path = self._download_image(image_url, self._unique_name("raw"))
        return self._remove_background(raw_path, self._unique_name("pet"))

    def _download_image(self, url: str, filename: str) -> str:
        response = httpx.get(url, timeout=60)
        response.raise_for_status()
        save_path = os.path.join(self._assets_dir, filename)
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path

    def _remove_background(self, input_path: str, output_filename: str) -> str:
        output_path = os.path.join(self._assets_dir, output_filename)
        try:
            with open(input_path, "rb") as f:
                input_data = f.read()
            output_data = remove(input_data, session=self._rembg_session)
            with open(output_path, "wb") as f:
                f.write(output_data)
        except Exception:
            # 内存不足时直接用原图
            import shutil
            shutil.copy2(input_path, output_path)
        return output_path
