from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.media import Media
from app.models.share_link import ShareLink

router = APIRouter()


class StatsResponse(BaseModel):
    movie_count: int
    tv_count: int
    anime_count: int
    variety_count: int
    total: int
    scraped_count: int
    pending_count: int


class RecentMedia(BaseModel):
    id: int
    title: str
    title_cn: Optional[str]
    poster_url: Optional[str]
    category: str
    created_at: str

    class Config:
        from_attributes = True


class StorageInfo(BaseModel):
    total: int
    used: int
    used_percent: float


class DashboardResponse(BaseModel):
    stats: StatsResponse
    recent: List[RecentMedia]
    storage: Optional[StorageInfo]


@router.get("/stats", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    movie_count = db.query(Media).filter(
        Media.user_id == current_user.id,
        Media.category == "movie"
    ).count()

    tv_count = db.query(Media).filter(
        Media.user_id == current_user.id,
        Media.category == "tv"
    ).count()

    anime_count = db.query(Media).filter(
        Media.user_id == current_user.id,
        Media.category == "anime"
    ).count()

    variety_count = db.query(Media).filter(
        Media.user_id == current_user.id,
        Media.category == "variety"
    ).count()

    scraped_count = db.query(Media).filter(
        Media.user_id == current_user.id,
        Media.status == "scraped"
    ).count()

    pending_count = db.query(Media).filter(
        Media.user_id == current_user.id,
        Media.status == "pending"
    ).count()

    return StatsResponse(
        movie_count=movie_count,
        tv_count=tv_count,
        anime_count=anime_count,
        variety_count=variety_count,
        total=movie_count + tv_count + anime_count + variety_count,
        scraped_count=scraped_count,
        pending_count=pending_count
    )


@router.get("/recent", response_model=List[RecentMedia])
async def get_recent(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    items = db.query(Media).filter(
        Media.user_id == current_user.id
    ).order_by(Media.created_at.desc()).limit(limit).all()

    return [
        RecentMedia(
            id=m.id,
            title=m.title,
            title_cn=m.title_cn,
            poster_url=m.poster_url,
            category=m.category,
            created_at=m.created_at.isoformat() if m.created_at else ""
        )
        for m in items
    ]


@router.get("/storage", response_model=StorageInfo)
async def get_storage(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    disk_config = current_user.get_disk_config()

    return StorageInfo(
        total=disk_config.get("storage_total", 0),
        used=disk_config.get("storage_used", 0),
        used_percent=disk_config.get("storage_used", 0) / max(disk_config.get("storage_total", 1), 1) * 100
    )
