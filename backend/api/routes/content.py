from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List

router = APIRouter()

class ScriptRequest(BaseModel):
    trend: str
    duration: int = 45
    style: str = "hook"

class ViralityRequest(BaseModel):
    script: str
    hashtags: List[str] = []
    platform: str = "instagram"

@router.post("/generate-script")
async def generate_script(request: ScriptRequest):
    if not request.trend:
        raise HTTPException(status_code=400, detail="Trend is required")
        
    return {
        "status": "success",
        "trend": request.trend,
        "duration": request.duration,
        "style": request.style,
        "hook": "Stop scrolling — AI just changed everything...",
        "story": "Here's what nobody's telling you about influence...",
        "insights": "Brands using AI see 3x engagement this quarter",
        "cta": "Follow @viranava for your AI creator playbook",
        "full_script": (
            "HOOK: Stop scrolling — AI just changed everything...\n"
            "STORY: Here's what nobody's telling you about influence...\n"
            "INSIGHTS: Brands using AI see 3x engagement this quarter\n"
            "CTA: Follow @viranava for your AI creator playbook"
        )
    }

@router.post("/predict-virality")
async def predict_virality(request: ViralityRequest):
    if not request.script:
        raise HTTPException(status_code=400, detail="Script is required")
        
    return {
        "status": "success",
        "virality_score": 87,
        "expected_views": "2.4M",
        "expected_likes": "180K",
        "expected_shares": "42K",
        "expected_saves": "38K",
        "grade": "High Viral Potential",
        "recommendation": "Publish Now ✓"
    }
