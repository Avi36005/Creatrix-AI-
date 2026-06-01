from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class AnalyzeRequest(BaseModel):
    handle: str
    platform: str = "instagram"

@router.post("/analyze")
async def analyze_influencer(request: AnalyzeRequest):
    if not request.handle:
        raise HTTPException(status_code=400, detail="Handle is required")
    
    # Mock analysis response aligned with Ankita's case study data
    if "ankita" in request.handle.lower():
        return {
            "status": "success",
            "handle": request.handle,
            "platform": request.platform,
            "ratefluencer_score": 94,
            "authenticity_score": 91,
            "growth_score": 88,
            "brand_match_score": 94,
            "details": {
                "followers": "2.4M",
                "engagement_rate": "6.8%",
                "post_frequency": "4.2/wk",
                "avg_views": "180K",
                "risk_profile": "low",
                "top_brand_matches": [
                    {"brand": "Nike", "score": 96},
                    {"brand": "Spotify", "score": 94},
                    {"brand": "Zara", "score": 88}
                ]
            }
        }
    
    # Fallback default score for any other handle
    return {
        "status": "success",
        "handle": request.handle,
        "platform": request.platform,
        "ratefluencer_score": 75,
        "authenticity_score": 82,
        "growth_score": 70,
        "brand_match_score": 78,
        "details": {
            "followers": "320K",
            "engagement_rate": "4.1%",
            "post_frequency": "2.5/wk",
            "avg_views": "25K",
            "risk_profile": "medium",
            "top_brand_matches": [
                {"brand": "Adidas", "score": 78},
                {"brand": "Apple", "score": 71}
            ]
        }
    }
