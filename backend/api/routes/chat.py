import sys
import os

from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from services.ai_providers.groq_client import GroqClient

router = APIRouter()

SYSTEM_PROMPT = (
    "You are Creatrix AI's helpful in-app assistant. "
    "Creatrix AI is an AI influencer-intelligence and viral-content platform: "
    "it analyzes any creator's REAL YouTube data to compute a Ratefluencer Score, "
    "detects fake followers, predicts growth, matches brands, discovers live trends, "
    "and generates reel scripts, LinkedIn posts, Instagram captions, and ElevenLabs voiceovers. "
    "Answer concisely and helpfully, guiding the user through the dashboard."
)


class ChatRequest(BaseModel):
    message: str
    history: List = []


@router.post("/")
async def chat(request: ChatRequest):
    try:
        # Fold recent turns into the prompt so Groq has conversation context.
        convo = ""
        for turn in (request.history or [])[-8:]:
            role = turn.get("role", "user") if isinstance(turn, dict) else "user"
            content = turn.get("content", "") if isinstance(turn, dict) else str(turn)
            if content:
                convo += f"{'User' if role == 'user' else 'Assistant'}: {content}\n"
        user = (convo + f"User: {request.message}\nAssistant:") if convo else request.message

        # Groq Llama 3.3 70B — fastest provider, ideal for chat (OpenAI fallback built in).
        reply = await GroqClient().complete(SYSTEM_PROMPT, user, max_tokens=500)
        if not reply or not reply.strip():
            reply = "I'm here to help! Please try again in a moment."
        return {"status": "success", "reply": reply.strip()}
    except Exception:
        return {
            "status": "success",
            "reply": "I'm here to help you navigate Creatrix AI! Please try again in a moment.",
        }
