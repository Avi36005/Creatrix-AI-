from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class DiscoverRequest(BaseModel):
    category: str = "tech"
    limit: int = 10

@router.post("/discover")
async def discover_trends(request: DiscoverRequest):
    # Standard mock trends returned from social signals
    return [
        {
            "trend": "AI replacing Content Creators",
            "category": "Tech",
            "score": 94,
            "growth_velocity": "+340%",
            "sources": ["Reddit", "LinkedIn", "YouTube"]
        },
        {
            "trend": "Micro-influencer ROI study",
            "category": "Marketing",
            "score": 88,
            "growth_velocity": "+185%",
            "sources": ["Twitter", "NewsAPI"]
        },
        {
            "trend": "Reels vs TikTok 2026",
            "category": "Social",
            "score": 81,
            "growth_velocity": "+120%",
            "sources": ["Instagram", "TikTok"]
        },
        {
            "trend": "Creator economy funding news",
            "category": "Finance",
            "score": 77,
            "growth_velocity": "+95%",
            "sources": ["NewsAPI", "Crunchbase"]
        },
        {
            "trend": "Brand UGC strategy shift",
            "category": "Brands",
            "score": 73,
            "growth_velocity": "+60%",
            "sources": ["LinkedIn", "Twitter"]
        }
    ]
