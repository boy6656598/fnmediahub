from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.share_link import ShareLink
from app.models.media import Media
from app.services.scrape_service import ScrapeService
from app.spiders.parser_factory import ParserFactory

router = APIRouter()


class ScrapeLinkRequest(BaseModel):
    url: str


class BatchScrapeRequest(BaseModel):
    urls: List[str]


class ScrapeSearchRequest(BaseModel):
    keyword: str
    media_type: str = "movie"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: Optional[int] = None
    result: Optional[dict] = None
    error: Optional[str] = None


@router.post("/link")
async def scrape_link(
    request: ScrapeLinkRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    parser = ParserFactory.get_parser(request.url)
    if not parser:
        raise HTTPException(status_code=400, detail="Unsupported share link platform")
    
    try:
        parse_result = await parser.parse(request.url)
        
        share_link = ShareLink(
            user_id=current_user.id,
            platform=parser.platform_name,
            url=request.url,
            status="success"
        )
        share_link.set_extracted_info(parse_result)
        db.add(share_link)
        db.commit()
        db.refresh(share_link)
        
        scrape_service = ScrapeService()
        media_info = await scrape_service.scrape_from_filename(
            parse_result.get("filename", parse_result.get("title", ""))
        )
        
        media = Media(
            user_id=current_user.id,
            share_link_id=share_link.id,
            title=media_info.get("title", parse_result.get("title", "")),
            title_cn=media_info.get("title_cn"),
            poster_url=media_info.get("poster_url"),
            backdrop_url=media_info.get("backdrop_url"),
            media_type=media_info.get("media_type", "movie"),
            year=media_info.get("year"),
            overview=media_info.get("overview"),
            tmdb_id=media_info.get("tmdb_id"),
            status="scraped"
        )
        db.add(media)
        db.commit()
        db.refresh(media)
        
        return {
            "share_link_id": share_link.id,
            "media_id": media.id,
            "media": media,
            "parse_result": parse_result,
            "scrape_result": media_info
        }
        
    except Exception as e:
        share_link = ShareLink(
            user_id=current_user.id,
            platform="unknown",
            url=request.url,
            status="failed",
            error_msg=str(e)
        )
        db.add(share_link)
        db.commit()
        raise HTTPException(status_code=500, detail=f"Scrape failed: {str(e)}")


@router.post("/batch")
async def batch_scrape(
    request: BatchScrapeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    results = []
    for url in request.urls:
        parser = ParserFactory.get_parser(url)
        if not parser:
            results.append({"url": url, "status": "failed", "error": "Unsupported platform"})
            continue
        
        try:
            parse_result = await parser.parse(url)
            share_link = ShareLink(
                user_id=current_user.id,
                platform=parser.platform_name,
                url=url,
                status="success"
            )
            share_link.set_extracted_info(parse_result)
            db.add(share_link)
            db.commit()
            
            scrape_service = ScrapeService()
            media_info = await scrape_service.scrape_from_filename(
                parse_result.get("filename", parse_result.get("title", ""))
            )
            
            media = Media(
                user_id=current_user.id,
                share_link_id=share_link.id,
                title=media_info.get("title", parse_result.get("title", "")),
                title_cn=media_info.get("title_cn"),
                poster_url=media_info.get("poster_url"),
                backdrop_url=media_info.get("backdrop_url"),
                media_type=media_info.get("media_type", "movie"),
                year=media_info.get("year"),
                overview=media_info.get("overview"),
                tmdb_id=media_info.get("tmdb_id"),
                status="scraped"
            )
            db.add(media)
            db.commit()
            
            results.append({
                "url": url,
                "status": "success",
                "media_id": media.id,
                "title": media.title
            })
        except Exception as e:
            results.append({"url": url, "status": "failed", "error": str(e)})
    
    return {"results": results}


@router.post("/search")
async def search_media(
    request: ScrapeSearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scrape_service = ScrapeService()
    results = await scrape_service.search_tmdb(request.keyword, request.media_type)
    return {"results": results}


@router.get("/status/{task_id}")
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    return TaskStatusResponse(
        task_id=task_id,
        status="completed",
        progress=100
    )
