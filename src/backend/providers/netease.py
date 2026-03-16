import httpx
from typing import List, Optional

from providers.base import BaseProvider, Song, Playlist, PlaybackState
from app.config import settings

class NeteaseProvider(BaseProvider):
    name = "netease"
    display_name = "网易云音乐"
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.client = None
        self.base_url = settings.NETEASE_API_URL
        self.cookie = None
    
    async def initialize(self):
        self.client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
    
    async def close(self):
        if self.client:
            await self.client.aclose()
    
    async def authenticate(self) -> bool:
        # 网易云使用 Cookie 认证，通过手机号登录获取
        return True
    
    def _convert_song(self, song: dict) -> Song:
        artists = [a.get('name') for a in song.get('ar', song.get('artists', []))]
        album = song.get('al', song.get('album', {}))
        return Song(
            id=f"netease:{song.get('id')}",
            title=song.get('name', 'Unknown'),
            artists=artists,
            album=album.get('name', '') if isinstance(album, dict) else str(album),
            duration=song.get('dt', song.get('duration', 0)) // 1000,
            cover_url=album.get('picUrl', '') if isinstance(album, dict) else '',
            platform="netease",
            platform_id=str(song.get('id')),
            external_urls={"netease": f"https://music.163.com/song?id={song.get('id')}"}
        )
    
    async def search(self, keyword: str, type: str = "track", limit: int = 10) -> List[Song]:
        try:
            type_map = {"track": 1, "album": 10, "artist": 100}
            response = await self.client.get(
                "/search",
                params={"keywords": keyword, "type": type_map.get(type, 1), "limit": limit}
            )
            data = response.json()
            songs = data.get('result', {}).get('songs', [])
            return [self._convert_song(s) for s in songs]
        except Exception as e:
            print(f"Netease search error: {e}")
            return []
    
    async def get_playback_url(self, song: Song) -> Optional[str]:
        try:
            response = await self.client.get(
                "/song/url",
                params={"id": song.platform_id, "br": 320000}
            )
            data = response.json()
            urls = data.get('data', [])
            return urls[0].get('url') if urls else None
        except Exception as e:
            print(f"Netease playback url error: {e}")
            return None
    
    async def get_playlists(self) -> List[Playlist]:
        try:
            # 需要登录后获取用户ID
            response = await self.client.get("/user/playlist", params={"uid": "user_id"})
            data = response.json()
            playlists = []
            for item in data.get('playlist', []):
                playlists.append(Playlist(
                    id=f"netease:{item.get('id')}",
                    name=item.get('name'),
                    description=item.get('description'),
                    cover_url=item.get('coverImgUrl'),
                    track_count=item.get('trackCount', 0),
                    platform="netease"
                ))
            return playlists
        except Exception as e:
            print(f"Netease playlists error: {e}")
            return []
    
    async def create_playlist(self, name: str, description: str = "") -> Playlist:
        try:
            response = await self.client.get(
                "/playlist/create",
                params={"name": name}
            )
            data = response.json()
            playlist = data.get('playlist', {})
            return Playlist(
                id=f"netease:{playlist.get('id')}",
                name=playlist.get('name'),
                platform="netease"
            )
        except Exception as e:
            print(f"Netease create playlist error: {e}")
            raise
    
    async def add_to_playlist(self, playlist_id: str, song: Song) -> bool:
        try:
            pid = playlist_id.replace("netease:", "")
            await self.client.get(
                "/playlist/tracks",
                params={"op": "add", "pid": pid, "tracks": song.platform_id}
            )
            return True
        except Exception as e:
            print(f"Netease add to playlist error: {e}")
            return False
    
    async def get_recommendations(self, seed_tracks: List[Song] = None, limit: int = 10) -> List[Song]:
        try:
            response = await self.client.get("/recommend/songs")
            data = response.json()
            songs = data.get('data', {}).get('dailySongs', [])
            return [self._convert_song(s) for s in songs[:limit]]
        except Exception as e:
            print(f"Netease recommendations error: {e}")
            return []
    
    async def like_song(self, song: Song, like: bool = True) -> bool:
        try:
            await self.client.get(
                "/like",
                params={"id": song.platform_id, "like": "true" if like else "false"}
            )
            return True
        except Exception as e:
            print(f"Netease like error: {e}")
            return False
    
    async def get_top_tracks(self, time_range: str = "medium", limit: int = 50) -> List[Song]:
        # 网易云没有直接的 top tracks API，可以从播放记录统计
        return []
    
    async def get_playback_state(self) -> PlaybackState:
        # 网易云 API 不提供实时播放状态
        return PlaybackState()
    
    async def control(self, action: str, **kwargs) -> bool:
        # 网易云 API 不提供播放控制
        return False
