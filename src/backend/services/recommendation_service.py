from typing import List, Dict
from collections import Counter
import random

from services.memory_service import MusicMemory
from models import Song

class RecommendationService:
    """音乐推荐服务"""
    
    def __init__(self, memory: MusicMemory):
        self.memory = memory
    
    async def recommend(self, count: int = 10, mood: str = None) -> List[Song]:
        """多策略推荐"""
        recommendations = []
        
        # 1. 基于历史的相似推荐 (30%)
        history_based = await self._recommend_by_history(count // 3)
        recommendations.extend(history_based)
        
        # 2. 基于偏好的探索推荐 (40%)
        prefs = self.memory.get_preferences()
        preference_based = await self._recommend_by_preferences(prefs, count // 3, mood)
        recommendations.extend(preference_based)
        
        # 3. 随机探索 (30%)
        explore_count = count - len(recommendations)
        if explore_count > 0:
            # 这里可以调用 provider 获取热门歌曲
            pass
        
        # 去重并限制数量
        seen_ids = set()
        unique_recs = []
        for song in recommendations:
            if song.id not in seen_ids:
                seen_ids.add(song.id)
                unique_recs.append(song)
        
        return unique_recs[:count]
    
    async def _recommend_by_history(self, count: int) -> List[Song]:
        """基于播放历史推荐"""
        history = self.memory.get_play_history(days=30, limit=100)
        if not history or count <= 0:
            return []
        
        # 提取常听艺术家
        all_artists = []
        for h in history:
            all_artists.extend(h.get("artists", []))
        
        top_artists = Counter(all_artists).most_common(5)
        # 这里可以基于这些艺术家搜索相似歌曲
        return []
    
    async def _recommend_by_preferences(self, prefs, count: int, mood: str = None) -> List[Song]:
        """基于偏好推荐"""
        # 根据 mood 和偏好流派推荐
        return []
    
    async def generate_daily_mix(self, count: int = 30) -> List[Song]:
        """生成每日推荐歌单"""
        return await self.recommend(count=count)
