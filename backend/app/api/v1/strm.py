from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.media import Media
from app.models.strm_file import STRMFile
from app.services.strm_service import STRMGenerator, STRMScanner

router = APIRouter()


class STRMGenerateRequest(BaseModel):
    episode: Optional[int] = None


class STRMScanRequest(BaseModel):
    directory: str = "/"


class STRMResponse(BaseModel):
    id: int
    file_path: str
    file_url: str
    episode: Optional[str]
    media_id: Optional[int]

    class Config:
        from_attributes = True


@router.post("/generate/{media_id}")
async def generate_strm(
    media_id: int,
    request: STRMGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    media = db.query(Media).filter(
        Media.id == media_id,
        Media.user_id == current_user.id
    ).first()

    if not media:
        raise HTTPException(status_code=404, detail="Media not found")

    generator = STRMGenerator(db)

    try:
        if media.media_type == "tv" or media.category == "tv":
            paths = await generator.generate_episodes(media)
            return {"success": True, "paths": paths, "count": len(paths)}
        else:
            path = await generator.generate_strm(media, request.episode)
            return {"success": True, "path": path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generate STRM failed: {str(e)}")


@router.post("/scan")
async def scan_strm(
    request: STRMScanRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scanner = STRMScanner(db)

    try:
        results = await scanner.scan_directory(current_user.id, request.directory)
        return {
            "success": True,
            "count": len(results),
            "files": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan STRM failed: {str(e)}")


@router.get("/list", response_model=List[STRMResponse])
async def list_strm(
    page: int = 1,
    page_size: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(STRMFile).filter(STRMFile.user_id == current_user.id)

    total = query.count()
    items = query.order_by(STRMFile.created_at.desc())\
                  .offset((page - 1) * page_size)\
                  .limit(page_size)\
                  .all()

    return items


@router.delete("/{strm_id}")
async def delete_strm(
    strm_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    strm = db.query(STRMFile).filter(
        STRMFile.id == strm_id,
        STRMFile.user_id == current_user.id
    ).first()

    if not strm:
        raise HTTPException(status_code=404, detail="STRM not found")

    try:
        import os
        from app.core.config import settings

        full_path = os.path.join(settings.DOWNLOAD_PATH, strm.file_path.lstrip("/"))
        if os.path.exists(full_path):
            os.remove(full_path)

        db.delete(strm)
        db.commit()

        return {"success": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete STRM failed: {str(e)}")
