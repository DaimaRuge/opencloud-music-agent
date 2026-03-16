from sqlalchemy import create_engine, Column, String, Integer, Boolean, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import json

Base = declarative_base()

class PlayHistory(Base):
    __tablename__ = "play_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    unified_id = Column(String, index=True)
    platform = Column(String, index=True)
    platform_id = Column(String)
    title = Column(String)
    artists = Column(Text)
    album = Column(String)
    duration = Column(Integer)
    played_at = Column(DateTime, default=datetime.now, index=True)
    duration_played = Column(Integer)
    completed = Column(Boolean, default=False)
    source = Column(String)

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

class PlaylistDB(Base):
    __tablename__ = "playlists"
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    cover_url = Column(String)
    platform = Column(String)
    external_id = Column(String)
    is_smart = Column(Boolean, default=False)
    smart_rules = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class PlaylistSong(Base):
    __tablename__ = "playlist_songs"
    
    playlist_id = Column(String, primary_key=True)
    song_id = Column(String, primary_key=True)
    position = Column(Integer)
    added_at = Column(DateTime, default=datetime.now)

class SongCache(Base):
    __tablename__ = "song_cache"
    
    unified_id = Column(String, primary_key=True)
    title = Column(String)
    artists = Column(Text)
    album = Column(String)
    duration = Column(Integer)
    cover_url = Column(String)
    platform_ids = Column(Text)
    isrc = Column(String)
    cached_at = Column(DateTime, default=datetime.now)

# Database setup
from app.config import settings

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
