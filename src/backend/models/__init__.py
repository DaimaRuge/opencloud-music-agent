from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

class Platform(str, Enum):
    SPOTIFY = "spotify"
    NETEASE = "netease"
    APPLE = "apple"
    YOUTUBE = "youtube"
    QQ = "qq"

class Song(BaseModel):
    id: str = Field(..., description="跨平台统一ID")
    title: str
    artists: List[str]
    album: str
    duration: int = Field(..., description="时长（秒）")
    cover_url: Optional[str] = None
    platform: Platform
    platform_id: str = Field(..., description="平台原始ID")
    playable: bool = True
    preview_url: Optional[str] = None
    external_urls: Dict[str, str] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True

class SongSearchResult(BaseModel):
    songs: List[Song]
    total: int
    platform: Optional[Platform] = None
    query: str

class PlaybackState(BaseModel):
    is_playing: bool = False
    current_song: Optional[Song] = None
    progress_ms: int = 0
    duration_ms: int = 0
    volume: int = 100
    repeat_mode: str = "off"
    shuffle: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

class Playlist(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    owner: str = ""
    tracks: List[Song] = Field(default_factory=list)
    track_count: int = 0
    platform: Platform
    is_public: bool = True
    is_smart: bool = False
    smart_rules: Optional[Dict] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = None
    is_public: bool = True

class UserPreferences(BaseModel):
    favorite_genres: List[str] = Field(default_factory=list)
    favorite_artists: List[str] = Field(default_factory=list)
    preferred_platforms: List[Platform] = Field(default_factory=list)
    auto_play: bool = True
    crossfade: bool = False
    audio_quality: str = "high"
