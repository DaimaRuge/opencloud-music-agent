from fastapi import APIRouter

router = APIRouter()

@router.get("/recommendations")
async def get_recommendations(count: int = 10, mood: Optional[str] = None):
    """获取推荐歌曲"""
    return {"songs": [], "count": count, "mood": mood}

@router.get("/daily-mix")
async def get_daily_mix():
    """获取每日推荐"""
    return {"songs": [], "name": "Daily Mix"}
