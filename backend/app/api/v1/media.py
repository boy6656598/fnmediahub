from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.media import Media

router = APIRouter()


class MediaResponse(BaseModel):
    id: int
    title: str
    title_cn: Optional[str]
    poster_url: Optional[str]
    backdrop_url: Optional[str]
    media_type: str
    year: Optional[int]
    overview: Optional[str]
    status: str
    play_position: int

    class Config:
        from_attributes = True


class MediaUpdate(BaseModel):
    title: Optional[str] = None
    title_cn: Optional[str] = None
    poster_url: Optional[str] = None
    backdrop_url: Optional[str] = None
    overview: Optional[str] = None


class MediaListResponse(BaseModel):
    items: List[MediaResponse]
    total: int
    page: int
    page_size: int


@router.get("", response_model=MediaListResponse)
async def get_media_list(
    page: int = 1,
    page_size: int = 20,
    media_type: Optional[str] = None,
    status: Optional[str] = None,
    keyword: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Media).filter(Media.user_id == current_user.id)
    
    if media_type:
        query = query.filter(Media.media_type == media_type)
    if status:
        query = query.filter(Media.status == status)
    if keyword:
        query = query.filter(
            or_(
                Media.title.ilike(f"%{keyword}%"),
                Media.title_cn.ilike(f"%{keyword}%")
            )
        )
    
    total = query.count()
    items = query.order_by(Media.created_at.desc())\
                 .offset((page - 1) * page_size)\
                 .limit(page_size)\
                 .all()
    
    return MediaListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{media_id}", response_model=MediaResponse)
async def get_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    media = db.query(Media).filter(
        Media.id == media_id,
        Media.user_id == current_user.id
    ).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return media


@router.put("/{media_id}", response_model=MediaResponse)
async def update_media(
    media_id: int,
    update_data: MediaUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    media = db.query(Media).filter(
        Media.id == media_id,
        Media.user_id == current_user.id
    ).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    for key, value in update_data.model_dump(exclude_unset=True).items():
        setattr(media, key, value)
    
    db.commit()
    db.refresh(media)
    return media


@router.delete("/{media_id}")
async def delete_media(
    media_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    media = db.query(Media).filter(
        Media.id == media_id,
        Media.user_id == current_user.id
    ).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    db.delete(media)
    db.commit()
    return {"message": "Media deleted successfully"}
