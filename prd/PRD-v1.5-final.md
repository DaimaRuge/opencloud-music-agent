# OpenCloud Music AI Agent - PRD v1.5
## 产品需求文档 终版 - 项目总结与开源组件方案

**版本**: v1.5  
**日期**: 2026-03-17  
**状态**: 交付阶段  

---

## 1. 完整开源组件方案清单

为了最大程度利用开源社区力量，本项目核心组件选型如下：

| 模块 | 选用开源项目 | 理由 |
|------|--------------|------|
| **AI Agent 框架** | OpenClaw SDK | 原生支持多渠道(飞书/Discord)，内置沙盒和工具调用 |
| **后端框架** | FastAPI | 异步支持好，性能高，API 自动生成 |
| **前端框架** | React + Tailwind | 社区成熟，组件丰富 |
| **音乐播放核心** | Howler.js | 优秀的 Web Audio API 封装，支持多格式无缝切换 |
| **网易云 API** | NeteaseCloudMusicApi | 维护活跃，支持云盘上传、每日推荐等高级功能 |
| **Spotify API** | Spotipy | 官方推荐 Python 库 |
| **统一网盘层** | Alist | 聚合多端网盘，统一 API 接口，方便上传下载 |
| **本地音频处理** | FFmpeg + Mutagen | 音频转码，ID3 标签解析标配 |
| **数据库** | SQLite/PostgreSQL | 足够支撑个人或小型群体使用 |

---

## 2. 系统核心流程总结

1. **输入阶段**: 用户通过 语音/飞书/Discord 表达意图。
2. **理解阶段**: OpenClaw Agent 分析语义，识别出（播放、搜索、上传、创作）等意图。
3. **记忆阶段**: Agent 查询独立挂载的 `music_memory.json` 获取用户偏好和历史上下文。
4. **服务阶段**:
   - 调用统一 Provider 层（聚合 Spotify、网易云等）。
   - 如果是 AI 创作，调用大模型和音乐生成 API。
   - 如果是网盘操作，调用 Alist 接口或网易云盘 API。
5. **输出阶段**: 返回卡片消息或在 Web 端直接开始音频流的播放。

---

## 3. 部署方案指南

### 3.1 Docker Compose 部署结构

```yaml
version: '3.8'

services:
  # 核心后端
  backend:
    build: ./src/backend
    ports: ["8000:8000"]
    volumes:
      - ./data:/app/data

  # 前端 UI
  frontend:
    build: ./src/frontend
    ports: ["3000:3000"]

  # 网易云非官方 API 服务
  netease-api:
    image: binaryify/netease_cloud_music_api
    ports: ["3001:3000"]

  # Alist 网盘聚合服务
  alist:
    image: xhofe/alist:latest
    ports: ["5244:5244"]
    volumes:
      - ./data/alist:/opt/alist/data
```

### 3.2 启动流程
1. `docker-compose up -d`
2. 访问 `http://localhost:5244` 配置 Alist（绑定阿里云盘或本地存储）。
3. 访问 `http://localhost:8000/docs` 配置 Spotify Token 等环境变量。
4. 访问 `http://localhost:3000` 进入用户操作界面。
5. 将 Agent Skill 注册到 OpenClaw 实例。

---

## 4. 后续迭代建议 (Post v1.0)

1. **版权风险规避**: 仅作为工具聚合个人合法的账号和音频，不提供公共破解下载服务。
2. **多模态增强**: 结合视觉模型，允许用户上传一张照片，Agent 自动生成匹配该画面氛围的歌曲。
3. **P2P 分享**: 允许两个用户的独立记忆体进行碰撞，自动生成 "你们都会喜欢的歌单"。

---
*文档全 5 版迭代完成。代码骨架已在仓库中初始化。*