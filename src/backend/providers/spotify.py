import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Optional

from providers.base import BaseProvider, Song, Playlist, PlaybackState
from app.config import settings

class SpotifyProvider(BaseProvider):
    name = "spotify"
    display_name = "Spotify"
    
    def __init__(self, config: dict = None):
        super().__init__(config)
        self.client = None
        self.auth_manager = None
    
    async def initialize(self):
        if not settings.SPOTIFY_CLIENT_ID:
            return
        self.auth_manager = SpotifyOAuth(
            client_id=settings.SPOTIFY_CLIENT_ID,
            client_secret=settings.SPOTIFY_CLIENT_SECRET,
            redirect_uri=settings.SPOTIFY_REDIRECT_URI,
            scope="user-read-playback-state user-modify-playback-state "
                  "playlist-read-private playlist-modify-private "
                  "user-top-read user-read-recently-played"
        )
        self.client = spotipy.Spotify(auth_manager=self.auth_manager)
    
    def _convert_track(self, track: dict) -> Song:
        if not track:
            return None
        return Song(
            id=f"spotify:{track.get('id')}",
            title=track.get('name', 'Unknown'),
            artists=[a.get('name') for a in track.get('artists', [])],
            album=track.get('album', {}).get('name', ''),
            duration=track.get('duration_ms', 0) // 1000,
            cover_url=track.get('album', {}).get('images', [{}])[0].get('url'),
            platform="spotify",
            platform_id=track.get('id'),
            preview_url=track.get('preview_url'),
            external_urls={"spotify": track.get('external_urls', {}).get('spotify', '')}
        )
    
    async def authenticate(self) -> bool:
        try:
            self.client.current_user()
            return True
        except:
            return False
    
    async def search(self, keyword: str, type: str = "track", limit: int = 10) -> List[Song]:
        try:
            result = self.client.search(q=keyword, type=type, limit=limit)
            tracks = result.get('tracks', {}).get('items', [])
            return [self._convert_track(t) for t in tracks if t]
        except Exception as e:
            print(f"Spotify search error: {e}")
            return []
    
    async def get_playback_url(self, song: Song) -> Optional[str]:
        return song.external_urls.get("spotify")
    
    async def get_playlists(self) -> List[Playlist]:
        try:
            results = self.client.current_user_playlists()
            playlists = []
            for item in results.get('items', []):
                playlists.append(Playlist(
                    id=f"spotify:{item.get('id')}",
                    name=item.get('name'),
                    description=item.get('description'),
                    cover_url=item.get('images', [{}])[0].get('url'),
                    owner=item.get('owner', {}).get('display_name', ''),
                    track_count=item.get('tracks', {}).get('total', 0),
                    platform="spotify"
                ))
            return playlists
        except Exception as e:
            print(f"Spotify playlists error: {e}")
            return []
    
    async def create_playlist(self, name: str, description: str = "") -> Playlist:
        try:
            user = self.client.current_user()
            result = self.client.user_playlist_create(
                user=user['id'],
                name=name,
                description=description
            )
            return Playlist(
                id=f"spotify:{result['id']}",
                name=result['name'],
                description=result.get('description'),
                platform="spotify"
            )
        except Exception as e:
            print(f"Spotify create playlist error: {e}")
            raise
    
    async def add_to_playlist(self, playlist_id: str, song: Song) -> bool:
        try:
            pid = playlist_id.replace("spotify:", "")
            self.client.playlist_add_items(pid, [song.platform_id])
            return True
        except Exception as e:
            print(f"Spotify add to playlist error: {e}")
            return False
    
    async def get_recommendations(self, seed_tracks: List[Song] = None, limit: int = 10) -> List[Song]:
        try:
            seed_ids = [s.platform_id for s in (seed_tracks or [])[:5]]
            result = self.client.recommendations(seed_tracks=seed_ids or None, limit=limit)
            return [self._convert_track(t) for t in result.get('tracks', [])]
        except Exception as e:
            print(f"Spotify recommendations error: {e}")
            return []
    
    async def like_song(self, song: Song, like: bool = True) -> bool:
        try:
            if like:
                self.client.current_user_saved_tracks_add([song.platform_id])
            else:
                self.client.current_user_saved_tracks_delete([song.platform_id])
            return True
        except Exception as e:
            print(f"Spotify like error: {e}")
            return False
    
    async def get_top_tracks(self, time_range: str = "medium_term", limit: int = 50) -> List[Song]:
        try:
            result = self.client.current_user_top_tracks(time_range=time_range, limit=limit)
            return [self._convert_track(t) for t in result.get('items', [])]
        except Exception as e:
            print(f"Spotify top tracks error: {e}")
            return []
    
    async def get_playback_state(self) -> PlaybackState:
        try:
            state = self.client.current_playback()
            if not state:
                return PlaybackState()
            
            current = None
            if state.get('item'):
                current = self._convert_track(state['item'])
            
            return PlaybackState(
                is_playing=state.get('is_playing', False),
                current_song=current,
                progress_ms=state.get('progress_ms', 0),
                duration_ms=state.get('item', {}).get('duration_ms', 0),
                volume=state.get('device', {}).get('volume_percent', 100),
            )
        except Exception as e:
            print(f"Spotify playback state error: {e}")
            return PlaybackState()
    
    async def control(self, action: str, **kwargs) -> bool:
        try:
            if action == "play":
                self.client.start_playback()
            elif action == "pause":
                self.client.pause_playback()
            elif action == "next":
                self.client.next_track()
            elif action == "previous":
                self.client.previous_track()
            elif action == "volume":
                self.client.volume(kwargs.get('volume', 50))
            return True
        except Exception as e:
            print(f"Spotify control error: {e}")
            return False
