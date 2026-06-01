"""
Real influencer data via the YouTube Data API v3 (free tier).

Given a company / creator name we:
  1. Search for the best-matching channel
  2. Pull real channel statistics (subscribers, total views, video count)
  3. Pull the channel's recent uploads and aggregate real per-video
     engagement (views / likes / comments) to derive an engagement rate.

All calls degrade gracefully: if no YOUTUBE_API_KEY is configured, or the
API errors out, the caller receives ``None`` and can fall back to other
sources. No fabricated numbers are returned from here.
"""
import sys
import os

import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.config import settings

_BASE = "https://www.googleapis.com/youtube/v3"


def _engagement_rate(views: int, likes: int, comments: int) -> float:
    """Engagement as (likes + comments) / views, expressed as a percentage."""
    if views <= 0:
        return 0.0
    return round((likes + comments) / views * 100, 2)


async def fetch_channel(query: str) -> dict | None:
    """
    Resolve ``query`` (a company / creator name or @handle) to a real YouTube
    channel and return live metrics. Returns ``None`` when unavailable.
    """
    if not settings.YOUTUBE_API_KEY:
        return None

    key = settings.YOUTUBE_API_KEY
    handle = query.strip().lstrip("@")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            channel_id = await _resolve_channel_id(client, key, handle)
            if not channel_id:
                return None

            # ── Channel-level statistics ──────────────────────────────────
            ch = await client.get(
                f"{_BASE}/channels",
                params={"part": "snippet,statistics", "id": channel_id, "key": key},
            )
            ch.raise_for_status()
            items = ch.json().get("items", [])
            if not items:
                return None
            info = items[0]
            snip = info.get("snippet", {})
            stats = info.get("statistics", {})

            subscribers = int(stats.get("subscriberCount", 0))
            total_views = int(stats.get("viewCount", 0))
            video_count = int(stats.get("videoCount", 0))

            # ── Recent uploads → real engagement ─────────────────────────
            recent = await _recent_video_stats(client, key, channel_id)

            return {
                "source": "youtube",
                "handle": snip.get("title", handle),
                "channel_id": channel_id,
                "description": snip.get("description", "")[:300],
                "thumbnail": snip.get("thumbnails", {}).get("default", {}).get("url", ""),
                "followers": subscribers,
                "total_views": total_views,
                "video_count": video_count,
                "engagement_rate": recent["engagement_rate"],
                "avg_likes": recent["avg_likes"],
                "avg_comments": recent["avg_comments"],
                "avg_views": recent["avg_views"],
                "post_frequency": recent["post_frequency"],
                "recent_videos": recent["videos"],
            }
    except Exception:
        return None


async def _resolve_channel_id(client: httpx.AsyncClient, key: str, handle: str) -> str | None:
    """Find the most relevant channel id for a free-text query / handle."""
    r = await client.get(
        f"{_BASE}/search",
        params={
            "part": "snippet",
            "q": handle,
            "type": "channel",
            "maxResults": 1,
            "key": key,
        },
    )
    r.raise_for_status()
    items = r.json().get("items", [])
    if not items:
        return None
    return items[0]["snippet"]["channelId"]


async def _recent_video_stats(client: httpx.AsyncClient, key: str, channel_id: str) -> dict:
    """Aggregate engagement across the channel's most recent uploads."""
    empty = {
        "engagement_rate": 0.0,
        "avg_likes": 0,
        "avg_comments": 0,
        "avg_views": 0,
        "post_frequency": 0.0,
        "videos": [],
    }

    search = await client.get(
        f"{_BASE}/search",
        params={
            "part": "snippet",
            "channelId": channel_id,
            "order": "date",
            "type": "video",
            "maxResults": 10,
            "key": key,
        },
    )
    search.raise_for_status()
    video_ids = [
        it["id"]["videoId"]
        for it in search.json().get("items", [])
        if it.get("id", {}).get("videoId")
    ]
    if not video_ids:
        return empty

    vids = await client.get(
        f"{_BASE}/videos",
        params={
            "part": "statistics,snippet",
            "id": ",".join(video_ids),
            "key": key,
        },
    )
    vids.raise_for_status()
    items = vids.json().get("items", [])
    if not items:
        return empty

    total_v = total_l = total_c = 0
    videos = []
    dates = []
    for v in items:
        s = v.get("statistics", {})
        views = int(s.get("viewCount", 0))
        likes = int(s.get("likeCount", 0))
        comments = int(s.get("commentCount", 0))
        total_v += views
        total_l += likes
        total_c += comments
        dates.append(v.get("snippet", {}).get("publishedAt", ""))
        videos.append({
            "title": v.get("snippet", {}).get("title", "")[:120],
            "views": views,
            "likes": likes,
            "comments": comments,
            "published_at": v.get("snippet", {}).get("publishedAt", ""),
        })

    n = len(items)
    avg_views = total_v // n
    avg_likes = total_l // n
    avg_comments = total_c // n

    return {
        "engagement_rate": _engagement_rate(avg_views, avg_likes, avg_comments),
        "avg_likes": avg_likes,
        "avg_comments": avg_comments,
        "avg_views": avg_views,
        "post_frequency": _posts_per_week(dates),
        "videos": videos,
    }


def _posts_per_week(iso_dates: list) -> float:
    """Estimate uploads/week from the spread of recent publish timestamps."""
    from datetime import datetime

    parsed = []
    for d in iso_dates:
        try:
            parsed.append(datetime.fromisoformat(d.replace("Z", "+00:00")))
        except (ValueError, AttributeError):
            continue
    if len(parsed) < 2:
        return 1.0
    span_days = (max(parsed) - min(parsed)).days or 1
    return round(len(parsed) / (span_days / 7.0), 1)
