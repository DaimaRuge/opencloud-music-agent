# OpenCloud Music AI Agent - PRD v1.4
## 产品需求文档 第五版 - AI 创作与深度集成

**版本**: v1.4  
**日期**: 2026-03-17  
**状态**: AI 设计阶段  

---

## 1. AI 创作模块设计

### 1.1 核心功能
- **歌词生成**: 基于用户提供的提示词（Prompt）、情绪、主题生成歌词。
- **旋律生成**: 生成纯音乐旋律片段。
- **完整歌曲生成**: 结合歌词和指定风格生成完整的带有人声的歌曲。
- **智能伴奏**: 提取上传音乐的人声或伴奏。

### 1.2 外部 AI API 集成方案

| 功能 | 推荐方案 | 备选方案 |
|------|----------|----------|
| 歌词生成 | Claude 3.5 Sonnet / GPT-4o | 智谱 GLM-4 / Kimi |
| 音乐生成 | Suno API / Udio | MusicGen (本地部署) |
| 人声分离 | Spleeter (开源库) | Demucs (开源库) |
| 音乐标签 | Essentia.js (前端提取) | 阿里云音视频 API |

### 1.3 交互工作流

1. **用户输入意图**: "写一首关于秋天落叶的爵士乐"
2. **LLM 解析**:
   - 提取参数: `theme=秋天落叶`, `style=爵士乐`
   - 调用歌词生成 API -> 返回生成的歌词
3. **音乐生成**:
   - Agent 请求用户确认歌词
   - 确认后，调用 Suno API，传入歌词和风格
   - 等待异步生成完成
4. **结果交付**:
   - 返回音频流 URL 给前端播放器
   - 询问是否加入收藏库

### 1.4 AI Service 代码结构

```python
# src/backend/services/ai_music_service.py
import httpx
from typing import Dict, Optional

class AIMusicService:
    def __init__(self, llm_api_key: str, suno_api_key: str):
        self.llm_client = httpx.AsyncClient(...)
        self.suno_client = httpx.AsyncClient(...)
        
    async def generate_lyrics(self, prompt: str, style: str) -> str:
        """调用大语言模型生成歌词"""
        system_prompt = f"你是一个专业的作词人。请根据主题 '{prompt}' 和风格 '{style}' 创作一首歌的歌词，包含主歌、副歌和桥段。"
        # ... LLM API 调用
        return lyrics
        
    async def generate_music(self, lyrics: str, style: str) -> Dict:
        """调用 AI 音乐生成 API"""
        payload = {
            "prompt": lyrics,
            "tags": style,
            "make_instrumental": False
        }
        # ... Suno API 调用
        return {"audio_url": "...", "status": "completed"}
```

---

## 2. 独立音乐记忆系统深化

用户要求记忆是独立的，可随时携带并植入不同 Agent。

### 2.1 记忆包规范 (Music Memory Bundle)

记忆包是一个标准化的 JSON 文件，或压缩包（包含 JSON 和小体积本地元数据）。

```json
// music_memory_profile.json
{
  "version": "1.0",
  "user_profile": {
    "id": "user_123",
    "created_at": "2026-03-17T00:00:00Z"
  },
  "preferences": {
    "favorite_genres": ["jazz", "electronic"],
    "ignored_artists": ["bad_artist_1"],
    "platform_priority": ["spotify", "netease"]
  },
  "history": [
    {
      "unified_id": "song_abc",
      "timestamp": "2026-03-17T12:00:00Z",
      "listen_duration": 180,
      "context": "working"
    }
  ],
  "favorites": [
    "unified_id_1", "unified_id_2"
  ]
}
```

### 2.2 记忆导入/导出流程

- **导出**: Agent 提供命令 `/export_music_memory`，后端查询 SQLite 数据库，生成标准 JSON，通过文件流下载。
- **导入**: 提供 `/import_music_memory`，解析 JSON 并覆盖或合并到当前 SQLite 数据库。

---

## 3. 本地音乐库与网盘同步

### 3.1 本地上传机制
- 前端实现文件拖拽上传 (支持 mp3, flac, wav)。
- 后端使用 `mutagen` 解析音频 ID3 标签（封面、歌手、专辑）。

### 3.2 网盘/云盘集成
- **目标网盘**: 阿里云盘 / OneDrive / 百度网盘
- **方案**:
  - 采用开源项目 `alist` 作为统一网盘挂载层。
  - Backend 通过 Alist 的 API 将本地文件传输到指定网盘目录。
  - `Netease Cloud Music` 支持官方的音乐云盘 API（`/user/cloud` 和 `/cloud` 上传接口）。

```python
# 上传到网易云音乐云盘示例
async def upload_to_netease_cloud(file_path: str):
    # 1. 检查文件元数据
    # 2. 调用 /cloud 接口
    pass
```

---

## 4. 全链路测试方案

### 4.1 单元测试 (pytest)
- 测试音乐搜索接口是否正确返回标准化 `Song` 对象。
- 测试播放链接解析是否成功。
- 测试记忆数据库的读写。

### 4.2 集成测试
- **Agent 测试**: 模拟用户语音转文本输入，测试 Intent Parser 是否正确路由到 `play_music` 或 `search_music`。
- **推荐算法测试**: 给定固定测试用户画像，验证推荐歌曲的流派分布。

*下一版 (v1.5) 将进行总结与交付规范*
