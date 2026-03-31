from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import engine, Base
from app.api.v1 import auth, media, scrape, transfer, player


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
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

app.include_router(auth.router, prefix="/api/v1/auth", tags=["认证"])
app.include_router(media.router, prefix="/api/v1/media", tags=["媒体"])
app.include_router(scrape.router, prefix="/api/v1/scrape", tags=["削刮"])
app.include_router(transfer.router, prefix="/api/v1/transfer", tags=["转存"])
app.include_router(player.router, prefix="/api/v1/player", tags=["播放"])


@app.get("/health")
async def health_check():
    return {"status": "ok"}
