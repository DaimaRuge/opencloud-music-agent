# OpenCloud Music AI Agent - PRD v1.3
## 产品需求文档 第四版 - 核心代码实现

**版本**: v1.3  
**日期**: 2026-03-17  
**状态**: 代码实现阶段  

---

## 1. 项目初始化

### 1.1 目录结构

```bash
opencloud-music-agent/
├── src/
│   ├── backend/
│   │   ├── app/
│   │   │   ├── __init__.py
│   │   │   ├── main.py
│   │   │   ├── config.py
│   │   │   ├── dependencies.py
│   │   │   └── routers/
│   │   │       ├── __init__.py
│   │   │       ├── search.py
│   │   │       ├── player.py
│   │   │       ├── playlists.py
│   │   │       ├── recommendations.py
│   │   │       └── statistics.py
│   │   ├── providers/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── spotify.py
│   │   │   ├── netease.py
│   │   │   └── youtube.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── search_service.py
│   │   │   ├── player_service.py
│   │   │   ├── recommendation_service.py
│   │   │   └── statistics_service.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── song.py
│   │   │   ├── playlist.py
│   │   │   └── user.py
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py
│   │   │   └── repositories/
│   │   └── requirements.txt
│   │
│   ├── skill/
│   │   ├── __init__.py
│   │   ├── music_skill.py
│   │   ├── intents.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── search_handler.py
│   │   │   ├── player_handler.py
│   │   │   └── playlist_handler.py
│   │   └── memory/
│   │       ├── __init__.py
│   │       └── music_memory.py
│   │
│   └── frontend/
│       ├── public/
│       ├── src/
│       │   ├── components/
│       │   ├── pages/
│       │   ├── hooks/
│       │   ├── store/
│       │   └── services/
│       ├── package.json
│       └── tailwind.config.js
│
├── docs/
├── prd/
├── tests/
├── docker-compose.yml
├── Dockerfile
└── README.md
```

### 1.2 依赖文件

```txt
# src/backend/requirements.txt
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
aiosqlite==0.19.0
aiohttp==3.9.1
httpx==0.26.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
redis==5.0.1
spotipy==2.23.0
ytmusicapi==1.4.2
mutagen==1.47.0
ffmpeg-python==0.2.0
openai==1.10.0
anthropic==0.18.0
numpy==1.26.3
scikit-learn==1.4.0
pytest==7.4.4
pytest-asyncio==0.23.3
black==23.12.1
```

```json
// src/frontend/package.json
{
  "name": "opencloud-music-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.21.3",
    "zustand": "^4.4.7",
    "axios": "^1.6.5",
    "howler": "^2.2.4",
    "react-howler": "^5.2.0",
    "@headlessui/react": "^1.7.18",
    "@heroicons/react": "^2.1.1",
    "tailwindcss": "^3.4.1",
    "autoprefixer": "^10.4.17",
    "postcss": "^8.4.33",
    "recharts": "^2.10.4",
    "date-fns": "^3.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.48",
    "@types/react-dom": "^18.2.18",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.11"
  }
}
```

---

## 2. 后端核心代码

### 2.1 FastAPI 主应用

```python
# src/backend/app/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import search, player, playlists, recommendations, statistics
from app.config import settings
from providers import ProviderManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时初始化
    app.state.providers = ProviderManager()
    await app.state.providers.initialize()
    yield
    # 关闭时清理
    await app.state.providers.close()

app = FastAPI(
    title="OpenCloud Music API",
    description="Multi-platform music aggregation API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境需要限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(player.router, prefix="/api/v1", tags=["player"])
app.include_router(playlists.router, prefix="/api/v1", tags=["playlists"])
app.include_router(recommendations.router, prefix="/api/v1", tags=["recommendations"])
app.include_router(statistics.router, prefix="/api/v1", tags=["statistics"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

# WebSocket 实时通信
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            # 处理 WebSocket 消息
            await websocket.send_json({"echo": data})
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 2.2 配置管理

```python
# src/backend/app/config.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # 应用配置
    APP_NAME: str = "OpenCloud Music"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./music.db"
    
    # Redis (可选)
    REDIS_URL: Optional[str] = None
    
    # Spotify
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/callback/spotify"
    
    # 网易云
    NETEASE_PHONE: Optional[str] = None
    NETEASE_PASSWORD: Optional[str] = None
    
    # Apple Music
    APPLE_TEAM_ID: Optional[str] = None
    APPLE_KEY_ID: Optional[str] = None
    APPLE_PRIVATE_KEY: Optional[str] = None
    
    # AI 服务
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
```

### 2.3 数据模型

```python
# src/backend/app/models/song.py
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
    is_playing: bool
    current_song: Optional[Song] = None
    progress_ms: int = 0
    duration_ms: int = 0
    volume: int = 100
    repeat_mode: str = "off"  # off, track, context
    shuffle: bool = False
    timestamp: datetime = Field(default_factory=datetime.now)

# src/backend/app/models/playlist.py
class Playlist(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    cover_url: Optional[str] = None
    owner: str
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

# src/backend/app/models/user.py
class UserPreferences(BaseModel):
    favorite_genres: List[str] = Field(default_factory=list)
    favorite_artists: List[str] = Field(default_factory=list)
    preferred_platforms: List[Platform] = Field(default_factory=list)
    auto_play: bool = True
    crossfade: bool = False
    audio_quality: str = "high"  # standard, high, lossless
```

### 2.4 Provider 实现 - Spotify

```python
# src/backend/providers/spotify.py
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from typing import List, Optional
from datetime import datetime

from providers.base import BaseProvider, Song, Playlist, PlaybackState
from app.config import settings

class SpotifyProvider(BaseProvider):
    name = "spotify"
    display_name = "Spotify"
    
    def __init__(self):
        self.client = None
        self.auth_manager = None
    
    async def initialize(self):
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
        """转换 Spotify track 到统一 Song 模型"""
        return Song(
            id=f"spotify:{track['id']}",
            title=track['name'],
            artists=[artist['name'] for artist in track['artists']],
            album=track['album']['name'],
            duration=track['duration_ms'] // 1000,
            cover_url=track['album']['images'][0]['url'] if track['album']['images'] else None,
            platform="spotify",
            platform_id=track['id'],
            preview_url=track.get('preview_url'),
            external_urls={"spotify": track['external_urls']['spotify']}
        )
    
    async def search(self, keyword: str, type: str = "track", limit: int = 10) -> List[Song]:
        try:
            result = self.client.search(q=keyword, type=type, limit=limit)
            tracks = result['tracks']['items']
            return [self._convert_track(track) for track in tracks]
        except Exception as e:
            print(f"Spotify search error: {e}")
            return []
    
    async def get_playback_url(self, song: Song) -> Optional[str]:
        # Spotify 需要 Premium 才能获取完整播放 URL
        # 返回外部链接，通过 Spotify 应用播放
        return song.external_urls.get("spotify")
    
    async def get_playlists(self) -> List[Playlist]:
        try:
            results = self.client.current_user_playlists()
            playlists = []
            for item in results['items']:
                playlist = Playlist(
                    id=f"spotify:{item['id']}",
                    name=item['name'],
                    description=item.get('description'),
                    cover_url=item['images'][0]['url'] if item['images'] else None,
                    owner=item['owner']['display_name'],
                    track_count=item['tracks']['total'],
                    platform="spotify"
                )
                playlists.append(playlist)
            return playlists
        except Exception as e:
            print(f"Spotify get playlists error: {e}")
            return []
    
    async def get_playback_state(self) -> PlaybackState:
        try:
            state = self.client.current_playback()
            if not state:
                return PlaybackState(is_playing=False)
            
            current_track = None
            if state.get('item'):
                current_track = self._convert_track(state['item'])
            
            return PlaybackState(
                is_playing=state['is_playing'],
                current_song=current_track,
                progress_ms=state['progress_ms'],
                duration_ms=state['item']['duration_ms'] if state.get('item') else 0,
                volume=state['device']['volume_percent'] if state.get('device') else 100,
                repeat_mode=state.get('repeat_state', 'off'),
                shuffle=state.get('shuffle_state', False)
            )
        except Exception as e:
            print(f"Spotify playback state error: {e}")
            return PlaybackState(is_playing=False)
    
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
                volume = kwargs.get('volume', 50)
                self.client.volume(volume)
            return True
        except Exception as e:
            print(f"Spotify control error: {e}")
            return False
    
    async def get_recommendations(self, seed_tracks: List[Song] = None, limit: int = 10) -> List[Song]:
        try:
            seed_ids = [s.platform_id for s in seed_tracks[:5]] if seed_tracks else []
            result = self.client.recommendations(
                seed_tracks=seed_ids,
                limit=limit
            )
            return [self._convert_track(track) for track in result['tracks']]
        except Exception as e:
            print(f"Spotify recommendations error: {e}")
            return []
```

### 2.5 数据库层

```python
# src/backend/db/database.py
from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.config import settings

Base = declarative_base()

class PlayHistory(Base):
    __tablename__ = "play_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unified_id = Column(String, index=True)
    platform = Column(String, index=True)
    platform_id = Column(String)
    title = Column(String)
    artists = Column(Text)  # JSON
    album = Column(String)
    duration = Column(Integer)
    played_at = Column(DateTime, default=datetime.now, index=True)
    duration_played = Column(Integer)
    completed = Column(Boolean, default=False)
    source = Column(String)  # search, recommendation, playlist

class Favorite(Base):
    __tablename__ = "favorites"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unified_id = Column(String, unique=True, index=True)
    platform = Column(String)
    platform_id = Column(String)
    title = Column(String)
    artists = Column(Text)
    album = Column(String)
    cover_url = Column(String)
    liked_at = Column(DateTime, default=datetime.now)

class Preference(Base):
    __tablename__ = "preferences"
    
    key = Column(String, primary_key=True)
    value = Column(Text)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

# 数据库引擎
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

---

## 3. Skill 层实现

```python
# src/skill/music_skill.py
from typing import Dict, Any
import httpx

class MusicSkill:
    """OpenClaw Music Skill"""
    
    name = "music"
    description = "跨平台音乐聚合 AI Agent"
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api/v1"):
        self.api_base = api_base_url
        self.client = httpx.AsyncClient(base_url=api_base_url)
    
    async def search(self, keyword: str, platform: str = None) -> str:
        """搜索音乐"""
        params = {"q": keyword}
        if platform:
            params["platform"] = platform
        
        response = await self.client.get("/search", params=params)
        data = response.json()
        
        if not data.get("songs"):
            return f"未找到与 '{keyword}' 相关的歌曲"
        
        songs = data["songs"][:5]  # 只显示前5首
        result = f"🎵 搜索 '{keyword}' 的结果:\n\n"
        for i, song in enumerate(songs, 1):
            artists = ", ".join(song["artists"])
            result += f"{i}. {song['title']} - {artists} ({song['platform']})\n"
        
        result += "\n💡 提示: 说 '播放第1首' 或 '播放 {歌名}' 来播放"
        return result
    
    async def play(self, song_name: str = None, index: int = None) -> str:
        """播放音乐"""
        if index:
            # 播放最近搜索的第 index 首
            pass  # 需要实现上下文记忆
        
        response = await self.client.post("/player/play", json={"song_name": song_name})
        if response.status_code == 200:
            return f"▶️ 开始播放: {song_name}"
        return "播放失败，请检查播放器状态"
    
    async def control(self, action: str) -> str:
        """播放控制"""
        action_map = {
            "暂停": "pause",
            "播放": "play",
            "下一首": "next",
            "上一首": "previous"
        }
        
        api_action = action_map.get(action, action)
        response = await self.client.post(f"/player/{api_action}")
        
        if response.status_code == 200:
            return f"✅ 已执行: {action}"
        return f"❌ 操作失败: {action}"
    
    async def recommend(self, count: int = 10) -> str:
        """获取推荐"""
        response = await self.client.get("/recommendations", params={"count": count})
        data = response.json()
        
        if not data.get("songs"):
            return "暂无推荐歌曲"
        
        result = "🎯 为你推荐:\n\n"
        for i, song in enumerate(data["songs"], 1):
            artists = ", ".join(song["artists"])
            result += f"{i}. {song['title']} - {artists}\n"
        
        return result
    
    async def stats(self, period: str = "week") -> str:
        """听歌统计"""
        response = await self.client.get("/statistics", params={"period": period})
        data = response.json()
        
        result = f"📊 听歌统计 ({period})\n\n"
        result += f"总播放次数: {data.get('total_plays', 0)}\n"
        result += f"总听歌时长: {data.get('total_duration', 0) // 60} 分钟\n\n"
        
        if data.get("top_songs"):
            result += "🔥 最常听歌曲:\n"
            for song in data["top_songs"][:5]:
                result += f"  • {song[0]} ({song[2]}次)\n"
        
        return result
```

---

## 4. 前端核心实现

### 4.1 播放器组件

```tsx
// src/frontend/src/components/MusicPlayer.tsx
import React, { useEffect, useState, useRef } from 'react';
import ReactHowler from 'react-howler';
import { useMusicStore } from '../store/musicStore';

export const MusicPlayer: React.FC = () => {
  const playerRef = useRef<ReactHowler>(null);
  const { currentSong, isPlaying, volume, progress, setProgress, togglePlay } = useMusicStore();
  
  const [duration, setDuration] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      if (isPlaying && playerRef.current) {
        setProgress(playerRef.current.seek());
      }
    }, 1000);
    
    return () => clearInterval(interval);
  }, [isPlaying, setProgress]);
  
  if (!currentSong) {
    return (
      <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4">
        <div className="text-center text-gray-400">未在播放</div>
      </div>
    );
  }
  
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };
  
  return (
    <div className="fixed bottom-0 left-0 right-0 bg-gray-900 text-white p-4">
      <ReactHowler
        ref={playerRef}
        src={currentSong.preview_url || ''}
        playing={isPlaying}
        volume={volume}
        onLoad={() => setDuration(playerRef.current?.duration() || 0)}
        onEnd={() => {/* 播放下一首 */}}
      />
      
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* 歌曲信息 */}
        <div className="flex items-center space-x-4">
          <img
            src={currentSong.cover_url}
            alt={currentSong.title}
            className="w-14 h-14 rounded-lg object-cover"
          />
          <div>
            <div className="font-medium">{currentSong.title}</div>
            <div className="text-sm text-gray-400">
              {currentSong.artists.join(', ')}
            </div>
          </div>
        </div>
        
        {/* 播放控制 */}
        <div className="flex items-center space-x-6">
          <button className="hover:text-green-400">
            <PreviousIcon />
          </button>
          <button
            onClick={togglePlay}
            className="w-10 h-10 bg-green-500 rounded-full flex items-center justify-center hover:bg-green-400"
          >
            {isPlaying ? <PauseIcon /> : <PlayIcon />}
          </button>
          <button className="hover:text-green-400">
            <NextIcon />
          </button>
        </div>
        
        {/* 进度条 */}
        <div className="flex items-center space-x-2 w-1/3">
          <span className="text-sm text-gray-400">{formatTime(progress)}</span>
          <input
            type="range"
            min={0}
            max={duration}
            value={progress}
            onChange={(e) => playerRef.current?.seek(Number(e.target.value))}
            className="flex-1 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
          />
          <span className="text-sm text-gray-400">{formatTime(duration)}</span>
        </div>
      </div>
    </div>
  );
};
```

### 4.2 状态管理

```typescript
// src/frontend/src/store/musicStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Song {
  id: string;
  title: string;
  artists: string[];
  album: string;
  cover_url: string;
  duration: number;
  preview_url?: string;
  platform: string;
}

interface MusicState {
  currentSong: Song | null;
  isPlaying: boolean;
  volume: number;
  progress: number;
  queue: Song[];
  
  // Actions
  setCurrentSong: (song: Song) => void;
  togglePlay: () => void;
  setVolume: (volume: number) => void;
  setProgress: (progress: number) => void;
  addToQueue: (song: Song) => void;
  nextSong: () => void;
  previousSong: () => void;
}

export const useMusicStore = create<MusicState>()(
  persist(
    (set, get) => ({
      currentSong: null,
      isPlaying: false,
      volume: 80,
      progress: 0,
      queue: [],
      
      setCurrentSong: (song) => set({ currentSong: song, isPlaying: true }),
      togglePlay: () => set((state) => ({ isPlaying: !state.isPlaying })),
      setVolume: (volume) => set({ volume }),
      setProgress: (progress) => set({ progress }),
      addToQueue: (song) => set((state) => ({ queue: [...state.queue, song] })),
      nextSong: () => {
        const { queue, currentSong } = get();
        if (queue.length > 0) {
          const [next, ...rest] = queue;
          set({ currentSong: next, queue: rest, isPlaying: true });
        }
      },
      previousSong: () => {
        // 实现上一首逻辑
      },
    }),
    {
      name: 'music-storage',
    }
  )
);
```

---

## 5. Docker 部署

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
COPY src/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY src/backend/app ./app
COPY src/backend/providers ./providers
COPY src/backend/services ./services
COPY src/backend/db ./db
COPY src/backend/models ./models

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./.env:/app/.env
    environment:
      - DATABASE_URL=sqlite:///data/music.db
    restart: unless-stopped

  frontend:
    build: ./src/frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    restart: unless-stopped

  # 可选: Redis 缓存
  redis:
    image: redis:7-alpine
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

---

*下一版 (v1.4) 将实现 AI 音乐创作和完整测试方案*
