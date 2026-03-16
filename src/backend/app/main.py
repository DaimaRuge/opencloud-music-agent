from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.routers import search, player, playlists, recommendations, statistics
from db.database import init_db
from providers import ProviderManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    app.state.providers = ProviderManager()
    await app.state.providers.initialize()
    yield
    # Shutdown
    await app.state.providers.close()

app = FastAPI(
    title="OpenCloud Music API",
    description="Multi-platform music aggregation API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router, prefix="/api/v1")
app.include_router(player.router, prefix="/api/v1")
app.include_router(playlists.router, prefix="/api/v1")
app.include_router(recommendations.router, prefix="/api/v1")
app.include_router(statistics.router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            await websocket.send_json({"echo": data})
    except:
        pass
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
