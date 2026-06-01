import sys
import os
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from core.config import settings


class OpenAIChatClient:
    BASE_URL = "https://api.openai.com/v1"
    MODEL = "gpt-4o-mini"

    async def complete(self, system: str, user: str, max_tokens: int = 1500) -> str:
        if not settings.OPENAI_API_KEY:
            return ""

        headers = {
            "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.MODEL,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "max_tokens": max_tokens,
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                r = await client.post(
                    f"{self.BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload,
                )
                r.raise_for_status()
                data = r.json()
                return data["choices"][0]["message"]["content"]
        except Exception:
            return ""


openai_chat_client = OpenAIChatClient()
