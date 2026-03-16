# OpenCloud Music AI Agent - PRD v1.2
## 产品需求文档 第三版 - 详细架构设计

**版本**: v1.2  
**日期**: 2026-03-17  
**状态**: 架构设计阶段  

---

## 1. 系统架构总览

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              用户交互层                                       │
├──────────────┬──────────────┬──────────────┬──────────────┬─────────────────┤
│    语音      │    飞书      │   Telegram   │   Discord    │    Web UI       │
│   (VAD+ASR)  │   (Bot+Card) │    (Bot)     │    (Bot)     │  (React+Player) │
└──────────────┴──────────────┴──────────────┴──────────────┴─────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OpenClaw Agent Core                                │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Music Agent Skill                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌───────────┐  │   │
│  │  │  Intent     │  │   Context   │  │   Memory    │  │  Action   │  │   │
│  │  │  Parser     │  │   Manager   │  │   System    │  │  Router   │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └───────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Backend API Service                               │
│  ┌──────────────┬──────────────┬──────────────┬──────────────────────────┐  │
│  │   REST API   │   WebSocket  │  Auth        │    Middleware            │  │
│  │   (FastAPI)  │  (Realtime)  │  (OAuth2)    │    (Rate/Log/Error)      │  │
│  └──────────────┴──────────────┴──────────────┴──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────┐
│   Provider Layer    │  │    Service Layer    │  │    Data Layer       │
├─────────────────────┤  ├─────────────────────┤  ├─────────────────────┤
│ ┌───────────────┐   │  │ ┌───────────────┐   │  │ ┌───────────────┐   │
│ │   Spotify     │   │  │ │   Search      │   │  │ │    SQLite     │   │
│ │   Provider    │   │  │ │   Service     │   │  │ │    (Local)    │   │
│ └───────────────┘   │  │ └───────────────┘   │  │ └───────────────┘   │
│ ┌───────────────┐   │  │ ┌───────────────┐   │  │ ┌───────────────┐   │
│ │   Netease     │   │  │ │   Playback    │   │  │ │   JSON File   │   │
│ │   Provider    │   │  │ │   Service     │   │  │ │   (Memory)    │   │
│ └───────────────┘   │  │ └───────────────┘   │  │ └───────────────┘   │
│ ┌───────────────┐   │  │ ┌───────────────┐   │  │ ┌───────────────┐   │
│ │   Apple       │   │  │ │   Playlist    │   │  │ │   Optional    │   │
│ │   Provider    │   │  │ │   Service     │   │  │ │   PostgreSQL  │   │
│ └───────────────┘   │  │ └───────────────┘   │  │ │   (Cloud)     │   │
│ ┌───────────────┐   │  │ ┌───────────────┐   │  │ └───────────────┘   │
│ │   YouTube     │   │  │ │   Recommend   │   │  │ ┌───────────────┐   │
│ │   Provider    │   │  │ │   Service     │   │  │ │   Redis       │   │
│ └───────────────┘   │  │ └───────────────┘   │  │ │   (Cache)     │   │
└─────────────────────┘  │ ┌───────────────┐   │  │ └───────────────┘   │
                         │ │   AI Music    │   │  └─────────────────────┘
                         │ │   Service     │   │
                         │ └───────────────┘   │
                         │ ┌───────────────┐   │
                         │ │   Statistics  │   │
                         │ │   Service     │   │
                         │ └───────────────┘   │
                         └─────────────────────┘
```

---

## 2. 核心模块设计

### 2.1 Agent Skill 模块 (music_skill.py)

```python
from openclaw import Skill, Intent, Context

class MusicSkill(Skill):
    name = "music"
    description = "跨平台音乐聚合 AI Agent"
    
    def __init__(self):
        self.providers = ProviderManager()
        self.memory = MusicMemory()
        self.recommender = MusicRecommender()
    
    # ========== 意图定义 ==========
    
    @Intent("search_music")
    async def handle_search(self, ctx: Context, keyword: str, platform: str = None):
        """
        搜索歌曲/专辑/歌手
        示例: "搜索周杰伦", "找一下 Spotify 上的 Love Story"
        """
        results = await self.providers.search(keyword, platform)
        await ctx.reply(self.format_search_results(results))
    
    @Intent("play_music")
    async def handle_play(self, ctx: Context, song_name: str = None, song_id: str = None):
        """
        播放音乐
        示例: "播放晴天", "播放刚才搜索的第一首"
        """
        if song_id:
            song = await self.memory.get_song(song_id)
        else:
            results = await self.providers.search(song_name)
            song = results[0] if results else None
        
        if song:
            playback_url = await self.providers.get_playback_url(song)
            await ctx.reply_play(song, playback_url)
            await self.memory.record_play(song)
        else:
            await ctx.reply("未找到歌曲")
    
    @Intent("control_playback")
    async def handle_control(self, ctx: Context, action: str):
        """
        播放控制
        示例: "暂停", "下一首", "音量调到 50"
        """
        await self.providers.control(action)
        await ctx.reply(f"已执行: {action}")
    
    @Intent("manage_playlist")
    async def handle_playlist(self, ctx: Context, action: str, name: str = None, songs: list = None):
        """
        歌单管理
        示例: "创建一个 workout 歌单", "把这首歌加到收藏"
        """
        if action == "create":
            playlist = await self.providers.create_playlist(name)
            await ctx.reply(f"已创建歌单: {playlist.name}")
        elif action == "add":
            await self.providers.add_to_playlist(name, songs)
            await ctx.reply("已添加歌曲")
    
    @Intent("get_recommendations")
    async def handle_recommend(self, ctx: Context, count: int = 10, mood: str = None):
        """
        获取推荐
        示例: "给我推荐 10 首歌", "推荐一些适合工作的音乐"
        """
        prefs = await self.memory.get_preferences()
        songs = await self.recommender.recommend(prefs, count, mood)
        await ctx.reply(self.format_song_list(songs))
    
    @Intent("show_statistics")
    async def handle_stats(self, ctx: Context, period: str = "week"):
        """
        查看听歌统计
        示例: "这周听了什么", "我的听歌报告"
        """
        stats = await self.memory.get_statistics(period)
        await ctx.reply(self.format_stats(stats))
    
    @Intent("ai_create_music")
    async def handle_ai_music(self, ctx: Context, prompt: str, style: str = None):
        """
        AI 音乐创作
        示例: "创作一首关于雨天的歌", "生成一段轻音乐"
        """
        await ctx.reply("正在创作音乐，请稍候...")
        result = await self.ai_music.generate(prompt, style)
        await ctx.reply(f"创作完成: {result.url}")
```

### 2.2 Provider 适配器架构

```python
# providers/base.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict
from pydantic import BaseModel

class Song(BaseModel):
    id: str
    title: str
    artists: List[str]
    album: str
    duration: int
    cover_url: str
    platform: str
    external_id: str
    playable: bool = True

class Playlist(BaseModel):
    id: str
    name: str
    description: str
    songs: List[Song]
    cover_url: str
    track_count: int
    platform: str

class PlaybackState(BaseModel):
    is_playing: bool
    current_song: Optional[Song]
    progress_ms: int
    volume: int

class BaseProvider(ABC):
    """音乐平台适配器基类"""
    
    name: str = "base"
    display_name: str = "Base Provider"
    
    def __init__(self, config: Dict):
        self.config = config
        self._session = None
    
    @abstractmethod
    async def authenticate(self) -> bool:
        """认证/刷新 Token"""
        pass
    
    @abstractmethod
    async def search(self, keyword: str, type: str = "track", limit: int = 10) -> List[Song]:
        """搜索"""
        pass
    
    @abstractmethod
    async def get_playback_url(self, song: Song) -> Optional[str]:
        """获取播放链接"""
        pass
    
    @abstractmethod
    async def get_playlists(self) -> List[Playlist]:
        """获取用户歌单"""
        pass
    
    @abstractmethod
    async def create_playlist(self, name: str, description: str = "") -> Playlist:
        """创建歌单"""
        pass
    
    @abstractmethod
    async def add_to_playlist(self, playlist_id: str, song: Song) -> bool:
        """添加歌曲到歌单"""
        pass
    
    @abstractmethod
    async def get_recommendations(self, seed_tracks: List[Song] = None, limit: int = 10) -> List[Song]:
        """获取推荐"""
        pass
    
    @abstractmethod
    async def like_song(self, song: Song, like: bool = True) -> bool:
        """喜欢/取消喜欢"""
        pass
    
    @abstractmethod
    async def get_top_tracks(self, time_range: str = "medium", limit: int = 50) -> List[Song]:
        """获取用户常听歌曲"""
        pass
    
    @abstractmethod
    async def get_playback_state(self) -> PlaybackState:
        """获取播放状态"""
        pass
    
    @abstractmethod
    async def control(self, action: str, **kwargs) -> bool:
        """播放控制"""
        pass

# providers/spotify.py
class SpotifyProvider(BaseProvider):
    name = "spotify"
    display_name = "Spotify"
    
    async def authenticate(self) -> bool:
        # OAuth2 流程
        pass
    
    async def search(self, keyword: str, type: str = "track", limit: int = 10) -> List[Song]:
        # 调用 Spotify Web API
        pass
    
    # ... 其他方法实现

# providers/netease.py
class NeteaseProvider(BaseProvider):
    name = "netease"
    display_name = "网易云音乐"
    
    async def authenticate(self) -> bool:
        # 手机登录/二维码登录
        pass
    
    # ... 其他方法实现
```

### 2.3 记忆系统架构

```python
# memory/music_memory.py
import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from pathlib import Path

class MusicMemory:
    """音乐记忆管理器"""
    
    def __init__(self, data_dir: str = "~/.openclaw/music-memory"):
        self.data_dir = Path(data_dir).expanduser()
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化数据库
        self.db_path = self.data_dir / "music.db"
        self._init_db()
    
    def _init_db(self):
        """初始化 SQLite 数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 播放记录表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS play_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                artists TEXT,
                played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                duration_played INTEGER,
                completed BOOLEAN DEFAULT FALSE
            )
        """)
        
        # 收藏表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                song_id TEXT NOT NULL,
                platform TEXT NOT NULL,
                title TEXT,
                artists TEXT,
                liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(song_id, platform)
            )
        """)
        
        # 用户偏好表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    async def record_play(self, song: Song, duration_played: int, completed: bool):
        """记录播放"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO play_history (song_id, platform, title, artists, duration_played, completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (song.id, song.platform, song.title, json.dumps(song.artists), duration_played, completed))
        conn.commit()
        conn.close()
    
    async def get_play_history(self, days: int = 7, limit: int = 100) -> List[Dict]:
        """获取播放历史"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        since = datetime.now() - timedelta(days=days)
        cursor.execute("""
            SELECT * FROM play_history 
            WHERE played_at > ? 
            ORDER BY played_at DESC 
            LIMIT ?
        """, (since, limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    async def update_preference(self, key: str, value: any):
        """更新偏好"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO preferences (key, value, updated_at)
            VALUES (?, ?, ?)
        """, (key, json.dumps(value), datetime.now()))
        conn.commit()
        conn.close()
    
    async def get_preferences(self) -> Dict:
        """获取所有偏好"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM preferences")
        results = cursor.fetchall()
        conn.close()
        return {k: json.loads(v) for k, v in results}
    
    async def get_statistics(self, period: str = "week") -> Dict:
        """获取听歌统计"""
        periods = {
            "day": 1,
            "week": 7,
            "month": 30,
            "year": 365
        }
        days = periods.get(period, 7)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        since = datetime.now() - timedelta(days=days)
        
        # 总播放次数
        cursor.execute("""
            SELECT COUNT(*), SUM(duration_played) 
            FROM play_history 
            WHERE played_at > ?
        """, (since,))
        total_plays, total_duration = cursor.fetchone()
        
        # 最常听歌曲
        cursor.execute("""
            SELECT title, artists, COUNT(*) as count
            FROM play_history 
            WHERE played_at > ?
            GROUP BY song_id
            ORDER BY count DESC
            LIMIT 10
        """, (since,))
        top_songs = cursor.fetchall()
        
        # 最常听平台
        cursor.execute("""
            SELECT platform, COUNT(*) as count
            FROM play_history 
            WHERE played_at > ?
            GROUP BY platform
        """, (since,))
        platform_dist = cursor.fetchall()
        
        conn.close()
        
        return {
            "period": period,
            "total_plays": total_plays or 0,
            "total_duration": total_duration or 0,
            "top_songs": top_songs,
            "platform_distribution": platform_dist
        }
```

### 2.4 推荐系统架构

```python
# services/recommendation.py
import numpy as np
from typing import List, Dict
from collections import Counter

class MusicRecommender:
    """音乐推荐引擎"""
    
    def __init__(self, memory: MusicMemory):
        self.memory = memory
    
    async def recommend(self, prefs: Dict, count: int = 10, mood: str = None) -> List[Song]:
        """
        多策略推荐
        - 协同过滤: 基于用户历史行为
        - 内容推荐: 基于歌曲特征
        - 热门推荐: 兜底策略
        """
        recommendations = []
        
        # 1. 基于历史的相似推荐 (30%)
        history_based = await self._recommend_by_history(count // 3)
        recommendations.extend(history_based)
        
        # 2. 基于偏好的探索推荐 (40%)
        preference_based = await self._recommend_by_preferences(prefs, count // 3)
        recommendations.extend(preference_based)
        
        # 3. 热门/趋势推荐 (30%)
        trending = await self._recommend_trending(count - len(recommendations))
        recommendations.extend(trending)
        
        return recommendations[:count]
    
    async def _recommend_by_history(self, count: int) -> List[Song]:
        """基于播放历史推荐相似歌曲"""
        history = await self.memory.get_play_history(days=30, limit=50)
        
        if not history:
            return []
        
        # 获取最近常听的歌手
        artists = []
        for record in history:
            artists.extend(json.loads(record[4]))  # artists 字段
        
        top_artists = Counter(artists).most_common(5)
        
        # 搜索这些歌手的其他歌曲
        # TODO: 调用 provider 搜索
        return []
    
    async def _recommend_by_preferences(self, prefs: Dict, count: int) -> List[Song]:
        """基于用户偏好推荐"""
        # 获取用户喜欢的流派
        favorite_genres = prefs.get("favorite_genres", [])
        
        # 根据流派推荐
        # TODO: 实现基于流派的推荐
        return []
    
    async def _recommend_trending(self, count: int) -> List[Song]:
        """推荐热门歌曲"""
        # TODO: 获取各平台热门榜单
        return []
    
    async def generate_daily_mix(self) -> List[Song]:
        """生成每日推荐歌单"""
        prefs = await self.memory.get_preferences()
        history = await self.memory.get_play_history(days=7)
        
        # 结合最近听歌和长期偏好
        songs = await self.recommend(prefs, count=30)
        
        return songs
```

---

## 3. API 设计

### 3.1 REST API 端点

```yaml
# API 概览

# 搜索
GET  /api/v1/search?q={keyword}&type={track|album|artist}&platform={platform}&limit={limit}

# 播放控制
POST /api/v1/player/play
POST /api/v1/player/pause
POST /api/v1/player/next
POST /api/v1/player/previous
POST /api/v1/player/volume?level={0-100}
GET  /api/v1/player/state

# 歌单
GET    /api/v1/playlists
POST   /api/v1/playlists
GET    /api/v1/playlists/{id}
PUT    /api/v1/playlists/{id}
DELETE /api/v1/playlists/{id}
POST   /api/v1/playlists/{id}/songs
DELETE /api/v1/playlists/{id}/songs/{song_id}

# 收藏
GET    /api/v1/favorites
POST   /api/v1/favorites
DELETE /api/v1/favorites/{song_id}

# 推荐
GET /api/v1/recommendations?count={count}&mood={mood}
GET /api/v1/daily-mix

# 统计
GET /api/v1/statistics?period={day|week|month|year}
GET /api/v1/history?days={days}&limit={limit}

# AI 音乐
POST /api/v1/ai/generate
POST /api/v1/ai/lyrics

# 用户
GET /api/v1/user/preferences
PUT /api/v1/user/preferences
GET /api/v1/user/top-tracks
GET /api/v1/user/top-artists
```

### 3.2 WebSocket 实时通信

```javascript
// WebSocket 事件
{
  // 播放状态更新
  "event": "playback_state_changed",
  "data": {
    "is_playing": true,
    "current_song": {...},
    "progress_ms": 12345,
    "volume": 80
  }
}

// 歌曲切换
{
  "event": "track_changed",
  "data": {
    "previous_song": {...},
    "current_song": {...}
  }
}

// 播放完成
{
  "event": "track_finished",
  "data": {
    "song": {...},
    "duration_played": 180000
  }
}
```

---

## 4. 数据库 Schema

```sql
-- 播放历史
CREATE TABLE play_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id TEXT NOT NULL,
    platform TEXT NOT NULL,
    title TEXT,
    artists TEXT, -- JSON array
    album TEXT,
    duration INTEGER, -- 歌曲总时长
    played_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    duration_played INTEGER, -- 实际播放时长
    completed BOOLEAN DEFAULT FALSE,
    source TEXT -- 播放来源: search, recommendation, playlist
);

-- 收藏
CREATE TABLE favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    unified_id TEXT UNIQUE, -- 跨平台统一ID
    platform TEXT NOT NULL,
    song_id TEXT NOT NULL,
    title TEXT,
    artists TEXT,
    album TEXT,
    cover_url TEXT,
    liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 歌单
CREATE TABLE playlists (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    cover_url TEXT,
    platform TEXT,
    external_id TEXT, -- 平台原始ID
    is_smart BOOLEAN DEFAULT FALSE, -- 是否智能歌单
    smart_rules TEXT, -- 智能歌单规则 (JSON)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 歌单歌曲关联
CREATE TABLE playlist_songs (
    playlist_id TEXT,
    song_id TEXT,
    position INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (playlist_id, song_id)
);

-- 用户偏好
CREATE TABLE preferences (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 歌曲元数据缓存
CREATE TABLE song_cache (
    unified_id TEXT PRIMARY KEY,
    title TEXT,
    artists TEXT,
    album TEXT,
    duration INTEGER,
    cover_url TEXT,
    platform_ids TEXT, -- JSON: {platform: song_id}
    isrc TEXT,
    cached_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

*下一版 (v1.3) 将实现核心代码和详细的前端设计*
