import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy.orm import Session

from db.database import SessionLocal, PlayHistory, Favorite, Preference, PlaylistDB, PlaylistSong
from models import Song, UserPreferences

class MusicMemory:
    """音乐记忆管理器 - 支持SQLite存储"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def record_play(self, song: Song, duration_played: int = 0, completed: bool = False, source: str = "search"):
        """记录播放历史"""
        history = PlayHistory(
            unified_id=song.id,
            platform=song.platform,
            platform_id=song.platform_id,
            title=song.title,
            artists=json.dumps(song.artists),
            album=song.album,
            duration=song.duration,
            duration_played=duration_played,
            completed=completed,
            source=source
        )
        self.db.add(history)
        self.db.commit()
    
    def get_play_history(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """获取播放历史"""
        since = datetime.now() - timedelta(days=days)
        results = self.db.query(PlayHistory).filter(
            PlayHistory.played_at > since
        ).order_by(PlayHistory.played_at.desc()).limit(limit).all()
        
        return [{
            "id": r.id,
            "song_id": r.unified_id,
            "title": r.title,
            "artists": json.loads(r.artists) if r.artists else [],
            "platform": r.platform,
            "played_at": r.played_at,
            "duration_played": r.duration_played,
            "completed": r.completed
        } for r in results]
    
    def add_favorite(self, song: Song):
        """添加收藏"""
        fav = Favorite(
            unified_id=song.id,
            platform=song.platform,
            platform_id=song.platform_id,
            title=song.title,
            artists=json.dumps(song.artists),
            album=song.album,
            cover_url=song.cover_url
        )
        self.db.merge(fav)
        self.db.commit()
    
    def remove_favorite(self, song_id: str):
        """取消收藏"""
        self.db.query(Favorite).filter(Favorite.unified_id == song_id).delete()
        self.db.commit()
    
    def get_favorites(self, limit: int = 100) -> List[Dict]:
        """获取收藏列表"""
        results = self.db.query(Favorite).order_by(Favorite.liked_at.desc()).limit(limit).all()
        return [{
            "id": r.unified_id,
            "title": r.title,
            "artists": json.loads(r.artists) if r.artists else [],
            "platform": r.platform,
            "cover_url": r.cover_url
        } for r in results]
    
    def update_preference(self, key: str, value):
        """更新用户偏好"""
        pref = Preference(key=key, value=json.dumps(value))
        self.db.merge(pref)
        self.db.commit()
    
    def get_preferences(self) -> UserPreferences:
        """获取用户偏好"""
        prefs = self.db.query(Preference).all()
        pref_dict = {p.key: json.loads(p.value) for p in prefs}
        return UserPreferences(
            favorite_genres=pref_dict.get("favorite_genres", []),
            favorite_artists=pref_dict.get("favorite_artists", []),
            preferred_platforms=pref_dict.get("preferred_platforms", ["spotify", "netease"])
        )
    
    def get_statistics(self, period: str = "week") -> Dict:
        """获取听歌统计"""
        periods = {"day": 1, "week": 7, "month": 30, "year": 365}
        days = periods.get(period, 7)
        since = datetime.now() - timedelta(days=days)
        
        # 基础统计
        total_plays = self.db.query(PlayHistory).filter(PlayHistory.played_at > since).count()
        total_duration = self.db.query(PlayHistory).filter(
            PlayHistory.played_at > since
        ).with_entities(func.sum(PlayHistory.duration_played)).scalar() or 0
        
        # Top songs
        from sqlalchemy import func
        top_songs = self.db.query(
            PlayHistory.title,
            PlayHistory.artists,
            func.count(PlayHistory.id).label("count")
        ).filter(PlayHistory.played_at > since).group_by(
            PlayHistory.unified_id
        ).order_by(func.count(PlayHistory.id).desc()).limit(10).all()
        
        # Platform distribution
        platform_dist = self.db.query(
            PlayHistory.platform,
            func.count(PlayHistory.id).label("count")
        ).filter(PlayHistory.played_at > since).group_by(PlayHistory.platform).all()
        
        return {
            "period": period,
            "total_plays": total_plays,
            "total_duration": total_duration,
            "top_songs": [(t.title, json.loads(t.artists) if t.artists else [], t.count) for t in top_songs],
            "platform_distribution": [(p.platform, p.count) for p in platform_dist]
        }
    
    def export_memory(self) -> Dict:
        """导出所有记忆为可移植格式"""
        prefs = self.get_preferences()
        favorites = self.get_favorites(limit=10000)
        history = self.get_play_history(days=365, limit=10000)
        
        return {
            "version": "1.0",
            "exported_at": datetime.now().isoformat(),
            "preferences": {
                "favorite_genres": prefs.favorite_genres,
                "favorite_artists": prefs.favorite_artists,
                "preferred_platforms": prefs.preferred_platforms
            },
            "favorites": favorites,
            "history": history
        }
    
    def import_memory(self, data: Dict):
        """导入记忆"""
        # 导入偏好
        if "preferences" in data:
            for key, value in data["preferences"].items():
                self.update_preference(key, value)
        
        # 导入收藏
        if "favorites" in data:
            for fav in data["favorites"]:
                # 转换为 Song 对象
                song = Song(
                    id=fav.get("id"),
                    title=fav.get("title"),
                    artists=fav.get("artists", []),
                    album="",
                    duration=0,
                    platform=fav.get("platform", "unknown"),
                    platform_id="",
                    cover_url=fav.get("cover_url")
                )
                self.add_favorite(song)

from sqlalchemy import func
