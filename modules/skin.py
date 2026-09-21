import os
import httpx
import replicate


class SkinGenerator:
    def __init__(self, replicate_api_key: str, assets_dir: str = "assets"):
        os.environ["REPLICATE_API_TOKEN"] = replicate_api_key
        self._assets_dir = assets_dir
        os.makedirs(assets_dir, exist_ok=True)

    def generate_from_description(self, description: str) -> str:
        prompt = f"cute desktop pet character, {description}, transparent background, chibi style, high quality PNG"
        output = replicate.run(
            "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
            input={
                "prompt": prompt,
                "negative_prompt": "background, shadow, blurry",
                "width": 512,
                "height": 512,
            },
        )
        image_url = output[0]
        return self._download_image(image_url, "custom_pet.png")

    def generate_from_image(self, image_path: str) -> str:
        with open(image_path, "rb") as f:
            output = replicate.run(
                "tencentarc/photomaker-style:467d062309da518648ba89d226490e02b8ed09b5abc15026e54e31c5a8cd0769",
                input={
                    "input_image": f,
                    "prompt": "cute chibi desktop pet character img, transparent background",
                    "style_name": "Anime",
                    "num_outputs": 1,
                },
            )
        image_url = output[0]
        return self._download_image(image_url, "custom_pet.png")

    def _download_image(self, url: str, filename: str) -> str:
        response = httpx.get(url, timeout=60)
        response.raise_for_status()
        save_path = os.path.join(self._assets_dir, filename)
        with open(save_path, "wb") as f:
            f.write(response.content)
        return save_path
