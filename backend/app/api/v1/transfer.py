from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.media import Media
from app.models.share_link import ShareLink
from app.services.transfer_service import TransferService
from app.services.disk_factory import DiskFactory

router = APIRouter()


class TransferStatusResponse(BaseModel):
    media_id: int
    status: str
    progress: Optional[int] = None
    file_path: Optional[str] = None
    error: Optional[str] = None


@router.post("/{media_id}")
async def transfer_media(
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
    
    if media.status == "ready" and media.file_path:
        return TransferStatusResponse(
            media_id=media_id,
            status="ready",
            progress=100,
            file_path=media.file_path
        )
    
    if media.status == "transferring":
        return TransferStatusResponse(
            media_id=media_id,
            status="transferring",
            progress=0
        )
    
    share_link = None
    if media.share_link_id:
        share_link = db.query(ShareLink).filter(ShareLink.id == media.share_link_id).first()
    
    try:
        disk_client = DiskFactory.create_disk_client(current_user)
        transfer_service = TransferService(disk_client)
        
        media.status = "transferring"
        db.commit()
        
        result = await transfer_service.transfer(media, share_link)
        
        media.status = "ready"
        media.file_path = result.get("file_path")
        media.file_size = result.get("file_size")
        db.commit()
        
        return TransferStatusResponse(
            media_id=media_id,
            status="ready",
            progress=100,
            file_path=result.get("file_path")
        )
        
    except Exception as e:
        media.status = "failed"
        db.commit()
        raise HTTPException(status_code=500, detail=f"Transfer failed: {str(e)}")


@router.get("/status/{media_id}", response_model=TransferStatusResponse)
async def get_transfer_status(
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
    
    return TransferStatusResponse(
        media_id=media_id,
        status=media.status,
        file_path=media.file_path if media.status == "ready" else None
    )


@router.get("/progress/{task_id}")
async def get_transfer_progress(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    return {
        "task_id": task_id,
        "progress": 100,
        "status": "completed"
    }
