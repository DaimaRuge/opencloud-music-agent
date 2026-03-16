# 🎵 OpenCloud Music AI Agent

基于 OpenClaw 生态的跨平台音乐聚合 AI Agent，支持 Spotify、网易云音乐等多平台，具备 AI 音乐创作和智能推荐能力。

## ✨ 核心功能

- 🔍 **跨平台搜索**: 一键搜索 Spotify、网易云音乐等平台
- 🎮 **播放控制**: 播放/暂停/切歌，支持多平台账号
- 📚 **歌单管理**: 创建、编辑、同步歌单
- ❤️ **收藏系统**: 统一管理喜欢的歌曲
- 📊 **听歌统计**: 记录播放历史，生成个人听歌报告
- 🤖 **AI 创作**: 使用 Suno API 创作音乐
- 💾 **独立记忆**: 可移植的音乐记忆系统

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/DaimaRuge/opencloud-music-agent.git
cd opencloud-music-agent
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 填入你的 API 密钥
```

### 3. Docker 启动
```bash
docker-compose up -d
```

访问 http://localhost:3000 使用 Web 界面

## 🏗️ 项目结构

```
opencloud-music-agent/
├── src/
│   ├── backend/          # FastAPI 后端
│   │   ├── app/          # FastAPI 应用
│   │   ├── providers/    # 音乐平台适配器
│   │   ├── services/     # 业务服务
│   │   ├── models/       # 数据模型
│   │   └── db/           # 数据库
│   ├── skill/            # OpenClaw Skill
│   └── frontend/         # React 前端
├── prd/                  # 产品需求文档
├── docker-compose.yml
└── README.md
```

## 📚 文档

- [PRD v1.0 - 概念与愿景](./prd/PRD-v1.0-concept.md)
- [PRD v1.1 - API 调研](./prd/PRD-v1.1-api-research.md)
- [PRD v1.2 - 架构设计](./prd/PRD-v1.2-architecture.md)
- [PRD v1.3 - 核心代码](./prd/PRD-v1.3-implementation.md)
- [PRD v1.4 - AI 创作](./prd/PRD-v1.4-ai-and-memory.md)
- [PRD v1.5 - 终版总结](./prd/PRD-v1.5-final.md)

## 🔧 开发

### 后端开发
```bash
cd src/backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 前端开发
```bash
cd src/frontend
npm install
npm run dev
```

## 📝 License

MIT
