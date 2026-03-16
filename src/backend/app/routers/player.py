from fastapi import APIRouter, HTTPException
from typing import Optional
from models import PlaybackState

router = APIRouter()

@router.post("/player/play")
async def play(song_id: Optional[str] = None, song_name: Optional[str] = None):
    """播放音乐"""
    return {"status": "playing", "song_id": song_id or song_name}

@router.post("/player/pause")
async def pause():
    """暂停播放"""
    return {"status": "paused"}

@router.post("/player/next")
async def next_track():
    """下一首"""
    return {"status": "next"}

@router.post("/player/previous")
async def previous_track():
    """上一首"""
    return {"status": "previous"}

@router.get("/player/state", response_model=PlaybackState)
async def get_playback_state():
    """获取播放状态"""
    return PlaybackState()
