from typing import List, Dict, Optional
from providers.base import BaseProvider, Song, Playlist
from providers.spotify import SpotifyProvider
from providers.netease import NeteaseProvider

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
    
    async def initialize(self):
        # Initialize all providers
        spotify = SpotifyProvider()
        await spotify.initialize()
        if await spotify.authenticate():
            self.providers["spotify"] = spotify
        
        netease = NeteaseProvider()
        await netease.initialize()
        self.providers["netease"] = netease
    
    async def close(self):
        for provider in self.providers.values():
            await provider.close()
    
    def get_provider(self, name: str) -> Optional[BaseProvider]:
        return self.providers.get(name)
    
    def list_providers(self) -> List[str]:
        return list(self.providers.keys())
    
    async def search_all(self, keyword: str, type: str = "track", limit: int = 10) -> List[Song]:
        """Search across all providers"""
        all_results = []
        for name, provider in self.providers.items():
            try:
                results = await provider.search(keyword, type, limit)
                all_results.extend(results)
            except Exception as e:
                print(f"Search error in {name}: {e}")
        return all_results[:limit * len(self.providers)]
    
    async def search(self, keyword: str, platform: str = None, **kwargs) -> List[Song]:
        if platform and platform in self.providers:
            return await self.providers[platform].search(keyword, **kwargs)
        return await self.search_all(keyword, **kwargs)
