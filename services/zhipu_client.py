from zhipuai import ZhipuAI


class ZhipuClient:
    MODEL = "glm-4-flash"

    def __init__(self, api_key: str):
        self._client = ZhipuAI(api_key=api_key)

    def chat(self, messages: list[dict]) -> str:
        response = self._client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
        )
        return response.choices[0].message.content

    def chat_stream(self, messages: list[dict]):
        response = self._client.chat.completions.create(
            model=self.MODEL,
            messages=messages,
            stream=True,
        )
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content:
                yield content
