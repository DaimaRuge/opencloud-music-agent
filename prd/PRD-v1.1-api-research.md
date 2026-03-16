# OpenCloud Music AI Agent - PRD v1.1
## 产品需求文档 第二版 - 平台 API 深度调研

**版本**: v1.1  
**日期**: 2026-03-17  
**状态**: API 调研阶段  

---

## 1. 平台 API 详细调研

### 1.1 Spotify Web API

#### 认证流程
```
OAuth 2.0 流程:
1. 用户授权 -> Authorization Code
2. 换取 Access Token + Refresh Token
3. Access Token 有效期 3600s
4. Refresh Token 永久有效（除非用户撤销）
```

#### 核心端点
| 功能 | Endpoint | 权限 |
|------|----------|------|
| 搜索 | GET /v1/search | 无需用户授权 |
| 获取播放状态 | GET /v1/me/player | user-read-playback-state |
| 控制播放 | PUT /v1/me/player/play | user-modify-playback-state |
| 获取歌单 | GET /v1/me/playlists | playlist-read-private |
| 创建歌单 | POST /v1/users/{user_id}/playlists | playlist-modify-private |
| 获取推荐 | GET /v1/recommendations | 无需用户授权 |
| 获取顶级曲目 | GET /v1/me/top/tracks | user-top-read |

#### 限制与配额
- 速率限制: 未记录具体数字，建议实现指数退避
- Web Playback SDK 需要 Premium
- 部分市场功能受限

#### 部署建议
```python
# 使用 spotipy 库
import spotipy
from spotipy.oauth2 import SpotifyOAuth

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    redirect_uri="http://localhost:8888/callback",
    scope="user-read-playback-state user-modify-playback-state playlist-read-private"
))
```

---

### 1.2 网易云音乐 API (非官方)

#### 项目信息
- **GitHub**: https://github.com/Binaryify/NeteaseCloudMusicApi
- **部署方式**: Node.js 服务器
- **Stars**: 30k+

#### 核心端点
| 功能 | Endpoint | 说明 |
|------|----------|------|
| 登录 | /login/cellphone | 手机登录 |
| 搜索 | /search | 关键词搜索 |
| 获取歌曲 URL | /song/url | 获取播放链接 |
| 获取歌单 | /playlist/detail | 歌单详情 |
| 获取每日推荐 | /recommend/songs | 每日推荐歌曲 |
| 私人 FM | /personal_fm | 私人 FM |
| 喜欢音乐 | /like | 喜欢/取消喜欢 |
| 获取歌词 | /lyric | 歌曲歌词 |

#### 部署方式
```bash
# Docker 部署
docker run -d -p 3000:3000 --name netease-api binaryify/netease_cloud_music_api

# 或本地部署
git clone https://github.com/Binaryify/NeteaseCloudMusicApi.git
cd NeteaseCloudMusicApi
npm install
npm start
```

#### 限制
- 非官方 API，可能有稳定性风险
- 需要处理登录 Cookie
- 部分接口需要特定 headers

---

### 1.3 QQ音乐 API

#### 官方 API
- **平台**: QQ音乐开放平台 (y.qq.com)
- **申请**: 需要企业资质审核
- **限制**: 个人开发者较难获取

#### 替代方案
- **UnblockMusic**: 部分开源项目提供逆向 API
- **限制**: 不稳定，不推荐生产环境使用

#### 建议策略
1. 优先申请官方 API
2. 备选: 使用网页版逆向（风险高）
3. 或者仅作为歌曲信息查询，播放跳转官方客户端

---

### 1.4 Apple Music API (MusicKit)

#### 认证方式
- **Developer Token**: JWT，有效期 6 个月
- **User Token**: 用户授权后获取

#### 核心功能
| 功能 | 支持度 | 说明 |
|------|--------|------|
| 目录搜索 | ✅ | 完整支持 |
| 播放控制 | ✅ | 需要 MusicKit JS |
| 获取歌单 | ✅ | 用户授权后 |
| 创建歌单 | ✅ | 需要授权 |
| 获取历史 | ⚠️ | 有限支持 |

#### 限制
- 需要 Apple Developer 账号 ($99/年)
- 主要面向 iOS/macOS 开发
- Web 端功能有限

---

### 1.5 其他平台

#### YouTube Music
- **ytmusicapi**: Python 非官方库
- **GitHub**: https://github.com/sigma67/ytmusicapi
- **特点**: 无需 API Key，使用登录 Cookie

#### 酷狗音乐 / 酷我音乐
- 官方 API 不开放
- 逆向方案不稳定
- 建议: 暂不集成

---

## 2. API 集成策略矩阵

| 平台 | 官方 API | 稳定性 | 功能完整度 | 推荐度 | 集成优先级 |
|------|----------|--------|------------|--------|------------|
| Spotify | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | P0 |
| 网易云 | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | P0 |
| Apple Music | ✅ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | P1 |
| YouTube Music | ❌ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | P1 |
| QQ音乐 | ⚠️ | ⭐⭐ | ⭐⭐ | ⭐⭐ | P2 |

---

## 3. 统一 API 抽象层设计

### 3.1 抽象接口
```python
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Song:
    id: str
    name: str
    artist: str
    album: str
    duration: int  # seconds
    cover_url: str
    platform: str  # spotify, netease, etc.
    external_id: str  # 平台原始ID

@dataclass
class Playlist:
    id: str
    name: str
    description: str
    songs: List[Song]
    cover_url: str
    platform: str

class MusicProvider(ABC):
    """音乐平台抽象基类"""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """平台名称"""
        pass
    
    @abstractmethod
    async def search(self, keyword: str, type: str = "song", limit: int = 10) -> List[Song]:
        """搜索歌曲/专辑/歌手"""
        pass
    
    @abstractmethod
    async def get_playback_url(self, song_id: str) -> Optional[str]:
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
    async def add_to_playlist(self, playlist_id: str, song_id: str) -> bool:
        """添加歌曲到歌单"""
        pass
    
    @abstractmethod
    async def get_recommendations(self, seed_tracks: List[str] = None) -> List[Song]:
        """获取推荐歌曲"""
        pass
    
    @abstractmethod
    async def like_song(self, song_id: str, like: bool = True) -> bool:
        """喜欢/取消喜欢歌曲"""
        pass
    
    @abstractmethod
    async def get_top_tracks(self, time_range: str = "medium_term", limit: int = 50) -> List[Song]:
        """获取用户常听歌曲"""
        pass
```

### 3.2 工厂模式
```python
class MusicProviderFactory:
    _providers = {}
    
    @classmethod
    def register(cls, name: str, provider_class: type):
        cls._providers[name] = provider_class
    
    @classmethod
    def create(cls, name: str, config: dict) -> MusicProvider:
        if name not in cls._providers:
            raise ValueError(f"Unknown provider: {name}")
        return cls._providers[name](config)
    
    @classmethod
    def list_providers(cls) -> List[str]:
        return list(cls._providers.keys())

# 注册平台
MusicProviderFactory.register("spotify", SpotifyProvider)
MusicProviderFactory.register("netease", NeteaseProvider)
MusicProviderFactory.register("apple", AppleMusicProvider)
```

---

## 4. 认证管理设计

### 4.1 Token 存储结构
```json
{
  "spotify": {
    "access_token": "xxx",
    "refresh_token": "xxx",
    "expires_at": 1234567890,
    "scope": "user-read-playback-state ..."
  },
  "netease": {
    "cookie": "xxx",
    "user_id": "xxx"
  },
  "apple": {
    "developer_token": "xxx",
    "user_token": "xxx",
    "expires_at": 1234567890
  }
}
```

### 4.2 自动刷新机制
```python
async def get_valid_token(provider: str) -> str:
    token_data = load_token(provider)
    
    if is_expired(token_data):
        if provider == "spotify":
            new_token = await refresh_spotify_token(token_data['refresh_token'])
        elif provider == "apple":
            new_token = generate_apple_developer_token()
        
        save_token(provider, new_token)
        return new_token['access_token']
    
    return token_data['access_token']
```

---

## 5. 数据模型设计

### 5.1 核心实体
```python
# 歌曲 (跨平台统一)
class UnifiedSong(BaseModel):
    id: str  # 内部统一ID
    title: str
    artists: List[str]
    album: str
    duration: int
    cover_url: str
    platform_sids: Dict[str, str]  # {platform: song_id}
    isrc: Optional[str]  # 国际标准录音代码

# 播放记录
class PlayRecord(BaseModel):
    song_id: str
    platform: str
    played_at: datetime
    duration_played: int  # 实际播放时长
    completed: bool  # 是否完整播放

# 用户偏好
class UserPreference(BaseModel):
    user_id: str
    favorite_genres: List[str]
    favorite_artists: List[str]
    preferred_platforms: List[str]  # 平台优先级
    play_time_distribution: Dict[str, int]  # 时段分布
```

---

## 6. 技术栈确定

### 6.1 后端
- **框架**: FastAPI (Python 3.11+)
- **数据库**: SQLite (本地) / PostgreSQL (可选云端)
- **ORM**: SQLAlchemy 2.0
- **异步**: asyncio + aiohttp
- **缓存**: aiocache (Redis 可选)

### 6.2 Agent/Skill
- **框架**: OpenClaw Agent SDK
- **技能开发**: Python Skill Template
- **记忆**: 本地 JSON + 可选云端同步

### 6.3 前端 (Web UI)
- **框架**: React 18 + TypeScript
- **样式**: Tailwind CSS
- **状态**: Zustand
- **播放器**: Howler.js / ReactPlayer

### 6.4 AI 音乐
- **音乐生成**: MusicGen (Meta) / Suno API
- **歌词生成**: GPT-4 / Claude
- **推荐**: 自研协同过滤 + 内容推荐

---

## 7. 项目结构

```
opencloud-music-agent/
├── src/
│   ├── agent/              # OpenClaw Agent Skill
│   │   ├── __init__.py
│   │   ├── music_skill.py  # 主 Skill 入口
│   │   ├── handlers/       # 意图处理器
│   │   └── memory/         # 记忆管理
│   │
│   ├── backend/            # FastAPI 后端
│   │   ├── api/            # API 路由
│   │   ├── providers/      # 音乐平台适配器
│   │   ├── services/       # 业务逻辑
│   │   ├── models/         # 数据模型
│   │   ├── db/             # 数据库
│   │   └── main.py
│   │
│   └── frontend/           # Web UI
│       ├── src/
│       ├── public/
│       └── package.json
│
├── docs/                   # 文档
├── prd/                    # 产品需求文档
├── tests/                  # 测试
└── docker-compose.yml
```

---

*下一版 (v1.2) 将进行详细架构设计和核心模块设计*
