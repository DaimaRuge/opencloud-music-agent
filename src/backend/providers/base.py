from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from pydantic import BaseModel

class Song(BaseModel):
    id: str
    title: str
    artists: List[str]
    album: str
    duration: int
    cover_url: Optional[str] = None
    platform: str
    platform_id: str
    playable: bool = True
    preview_url: Optional[str] = None
    external_urls: Dict[str, str] = {}

class Playlist(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    owner: str = ""
    songs: List[Song] = []
    track_count: int = 0
    platform: str

class PlaybackState(BaseModel):
    is_playing: bool = False
    current_song: Optional[Song] = None
    progress_ms: int = 0
    duration_ms: int = 0
    volume: int = 100

class BaseProvider(ABC):
    name: str = "base"
    display_name: str = "Base Provider"
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self._session = None
    
    @abstractmethod
    async def initialize(self):
        pass
    
    @abstractmethod
    async def authenticate(self) -> bool:
        pass
    
    @abstractmethod
    async def search(self, keyword: str, type: str = "track", limit: int = 10) -> List[Song]:
        pass
    
    @abstractmethod
    async def get_playback_url(self, song: Song) -> Optional[str]:
        pass
    
    @abstractmethod
    async def get_playlists(self) -> List[Playlist]:
        pass
    
    @abstractmethod
    async def create_playlist(self, name: str, description: str = "") -> Playlist:
        pass
    
    @abstractmethod
    async def add_to_playlist(self, playlist_id: str, song: Song) -> bool:
        pass
    
    @abstractmethod
    async def get_recommendations(self, seed_tracks: List[Song] = None, limit: int = 10) -> List[Song]:
        pass
    
    @abstractmethod
    async def like_song(self, song: Song, like: bool = True) -> bool:
        pass
    
    @abstractmethod
    async def get_top_tracks(self, time_range: str = "medium", limit: int = 50) -> List[Song]:
        pass
    
    @abstractmethod
    async def get_playback_state(self) -> PlaybackState:
        pass
    
    @abstractmethod
    async def control(self, action: str, **kwargs) -> bool:
        pass
    
    async def close(self):
        pass
