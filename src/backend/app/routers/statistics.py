from fastapi import APIRouter
from typing import Optional

router = APIRouter()

@router.get("/statistics")
async def get_statistics(period: str = "week"):
    """获取听歌统计"""
    return {
        "period": period,
        "total_plays": 0,
        "total_duration": 0,
        "top_songs": [],
        "platform_distribution": []
    }

@router.get("/history")
async def get_history(days: int = 7, limit: int = 100):
    """获取播放历史"""
    return {"history": [], "days": days, "limit": limit}
