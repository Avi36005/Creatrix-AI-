import httpx
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

VOICE_ID_DEFAULT = "EXAVITQu4vr4xnSDxMaL"  # Rachel

async def generate_voiceover(text: str, voice_id: str = VOICE_ID_DEFAULT) -> bytes:
    if not settings.ELEVENLABS_API_KEY:
        return b""
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    headers = {
        "xi-api-key": settings.ELEVENLABS_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "text": text[:2500],
        "model_id": "eleven_turbo_v2",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            r = await client.post(url, headers=headers, json=payload)
            r.raise_for_status()
            return r.content
    except Exception:
        return b""

AVAILABLE_VOICES = [
    {"id": "EXAVITQu4vr4xnSDxMaL", "name": "Rachel", "style": "calm"},
    {"id": "TxGEqnHWrfWFTfGW9XjX", "name": "Josh", "style": "deep"},
    {"id": "AZnzlk1XvdvUeBnXmlld", "name": "Domi", "style": "energetic"},
    {"id": "MF3mGyEYCl7XYWbV9V6O", "name": "Elli", "style": "friendly"},
]
