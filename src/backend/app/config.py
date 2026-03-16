from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    APP_NAME: str = "OpenCloud Music"
    DEBUG: bool = False
    SECRET_KEY: str = "your-secret-key-change-in-production"
    DATABASE_URL: str = "sqlite:///./music.db"
    REDIS_URL: Optional[str] = None
    
    # Spotify
    SPOTIFY_CLIENT_ID: Optional[str] = None
    SPOTIFY_CLIENT_SECRET: Optional[str] = None
    SPOTIFY_REDIRECT_URI: str = "http://localhost:8000/callback/spotify"
    
    # Netease
    NETEASE_PHONE: Optional[str] = None
    NETEASE_PASSWORD: Optional[str] = None
    NETEASE_API_URL: str = "http://localhost:3000"
    
    # Apple Music
    APPLE_TEAM_ID: Optional[str] = None
    APPLE_KEY_ID: Optional[str] = None
    APPLE_PRIVATE_KEY: Optional[str] = None
    
    # AI Services
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    SUNO_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
