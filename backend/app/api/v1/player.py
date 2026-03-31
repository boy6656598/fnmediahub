from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.media import Media
from app.services.disk_factory import DiskFactory

router = APIRouter()


class PlayerPositionUpdate(BaseModel):
    position: int


@router.get("/{media_id}/stream")
async def get_stream_url(
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
    
    if media.status != "ready" or not media.file_path:
        raise HTTPException(status_code=400, detail="Media not ready for playback")
    
    disk_client = DiskFactory.create_disk_client(current_user)
    
    try:
        stream_url = await disk_client.get_file_url(media.file_path)
        return {
            "stream_url": stream_url,
            "play_position": media.play_position,
            "file_size": media.file_size
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stream URL: {str(e)}")


@router.put("/{media_id}/position")
async def update_play_position(
    media_id: int,
    update: PlayerPositionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    media = db.query(Media).filter(
        Media.id == media_id,
        Media.user_id == current_user.id
    ).first()
    
    if not media:
        raise HTTPException(status_code=404, detail="Media not found")
    
    media.play_position = update.position
    db.commit()
    
    return {"message": "Position updated", "position": update.position}


@router.get("/{media_id}/subtitles")
async def get_subtitles(
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
    
    return {"subtitles": []}
