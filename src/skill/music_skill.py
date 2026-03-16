from typing import Dict, Any
import httpx

class MusicSkill:
    """OpenClaw Music Skill"""
    
    name = "music"
    description = "跨平台音乐聚合 AI Agent"
    
    def __init__(self, api_base_url: str = "http://localhost:8000/api/v1"):
        self.api_base = api_base_url
        self.client = httpx.AsyncClient(base_url=api_base_url, timeout=30.0)
    
    async def search(self, keyword: str, platform: str = None) -> str:
        """搜索音乐"""
        params = {"q": keyword}
        if platform:
            params["platform"] = platform
        
        try:
            response = await self.client.get("/search", params=params)
            data = response.json()
            
            if not data.get("songs"):
                return f"未找到与 '{keyword}' 相关的歌曲"
            
            songs = data["songs"][:5]
            result = f"🎵 搜索 '{keyword}' 的结果:\n\n"
            for i, song in enumerate(songs, 1):
                artists = ", ".join(song.get("artists", []))
                result += f"{i}. {song.get('title')} - {artists} ({song.get('platform')})\n"
            
            result += "\n💡 提示: 说 '播放第1首' 来播放"
            return result
        except Exception as e:
            return f"搜索出错: {str(e)}"
    
    async def play(self, song_name: str = None, index: int = None) -> str:
        """播放音乐"""
        try:
            response = await self.client.post("/player/play", json={"song_name": song_name})
            if response.status_code == 200:
                return f"▶️ 开始播放: {song_name or '音乐'}"
            return "播放失败"
        except Exception as e:
            return f"播放出错: {str(e)}"
    
    async def control(self, action: str) -> str:
        """播放控制"""
        action_map = {
            "暂停": "pause", "播放": "play",
            "下一首": "next", "上一首": "previous"
        }
        
        api_action = action_map.get(action, action)
        try:
            response = await self.client.post(f"/player/{api_action}")
            return f"✅ 已执行: {action}" if response.status_code == 200 else f"❌ 失败"
        except Exception as e:
            return f"控制出错: {str(e)}"
    
    async def recommend(self, count: int = 10) -> str:
        """获取推荐"""
        try:
            response = await self.client.get("/recommendations", params={"count": count})
            data = response.json()
            
            if not data.get("songs"):
                return "暂无推荐歌曲"
            
            result = "🎯 为你推荐:\n\n"
            for i, song in enumerate(data["songs"][:10], 1):
                artists = ", ".join(song.get("artists", []))
                result += f"{i}. {song.get('title')} - {artists}\n"
            return result
        except Exception as e:
            return f"获取推荐出错: {str(e)}"
    
    async def stats(self, period: str = "week") -> str:
        """听歌统计"""
        try:
            response = await self.client.get("/statistics", params={"period": period})
            data = response.json()
            
            result = f"📊 听歌统计 ({period})\n\n"
            result += f"总播放次数: {data.get('total_plays', 0)}\n"
            result += f"总听歌时长: {data.get('total_duration', 0) // 60} 分钟\n\n"
            
            top_songs = data.get("top_songs", [])
            if top_songs:
                result += "🔥 最常听歌曲:\n"
                for song in top_songs[:5]:
                    result += f"  • {song[0]} ({song[2]}次)\n"
            
            return result
        except Exception as e:
            return f"获取统计出错: {str(e)}"
    
    async def handle_intent(self, intent: str, **kwargs) -> str:
        """处理意图"""
        if intent == "search":
            return await self.search(kwargs.get("keyword"), kwargs.get("platform"))
        elif intent == "play":
            return await self.play(kwargs.get("song_name"))
        elif intent == "control":
            return await self.control(kwargs.get("action"))
        elif intent == "recommend":
            return await self.recommend(kwargs.get("count", 10))
        elif intent == "stats":
            return await self.stats(kwargs.get("period", "week"))
        else:
            return f"未知意图: {intent}"
