import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import settings
from api.routes import influencer, content, trends, agent

app = FastAPI(
    title="Creatrix AI — ViraNova API",
    version="1.0.0",
    description="AI-powered influencer intelligence + viral content creation platform",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(influencer.router, prefix="/api/v1/influencer", tags=["Influencer"])
app.include_router(content.router,    prefix="/api/v1/content",    tags=["Content"])
app.include_router(trends.router,     prefix="/api/v1/trends",     tags=["Trends"])
app.include_router(agent.router,      prefix="/api/v1/agent",      tags=["Agent"])


@app.on_event("startup")
async def startup_event():
    print("=" * 60)
    print("Creatrix AI — ViraNova API starting up")
    print(f"  Environment : {settings.APP_ENV}")
    print(f"  Port        : {settings.PORT}")
    print(f"  Claude key  : {'configured' if settings.ANTHROPIC_API_KEY and not settings.ANTHROPIC_API_KEY.startswith('sk-ant-...') else 'not configured (using fallbacks)'}")
    print(f"  Groq key    : {'configured' if settings.GROQ_API_KEY and not settings.GROQ_API_KEY.startswith('gsk_...') else 'not configured'}")
    print("=" * 60)


@app.get("/health")
def health():
    return {
        "status": "Creatrix AI is live",
        "version": "1.0.0",
        "env": settings.APP_ENV,
    }


@app.get("/")
def root():
    return {
        "name": "Creatrix AI — ViraNova API",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "influencer_analyze": "POST /api/v1/influencer/analyze",
            "content_script": "POST /api/v1/content/generate-script",
            "virality": "POST /api/v1/content/predict-virality",
            "linkedin": "POST /api/v1/content/linkedin",
            "instagram": "POST /api/v1/content/instagram",
            "trends": "POST /api/v1/trends/discover",
            "agent": "POST /api/v1/agent/run",
        },
    }
