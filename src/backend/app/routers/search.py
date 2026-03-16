from fastapi import APIRouter, Depends, HTTPException
from typing import Optional

from providers import ProviderManager
from models import SongSearchResult

router = APIRouter()

@router.get("/search", response_model=SongSearchResult)
async def search_music(
    q: str,
    platform: Optional[str] = None,
    type: str = "track",
    limit: int = 10,
    providers: ProviderManager = None
):
    """搜索音乐"""
    if not providers:
        raise HTTPException(status_code=503, detail="Providers not initialized")
    
    results = await providers.search(q, platform=platform, type=type, limit=limit)
    return SongSearchResult(
        songs=results,
        total=len(results),
        platform=platform,
        query=q
    )
