from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.clean_task import CleanTask
from app.services.task_scheduler import get_task_scheduler

router = APIRouter()


class CleanTaskConfig(BaseModel):
    schedule_type: str = "daily"
    hour: int = 3
    day_of_week: str = "sun"
    day_of_month: int = 1
    keep_count: int = 5
    transfer_dir: str = "/media/转存"


class CleanTaskResponse(BaseModel):
    id: int
    task_type: str
    last_run: Optional[datetime]
    next_run: Optional[datetime]
    status: str
    config: dict

    class Config:
        from_attributes = True


@router.get("", response_model=CleanTaskResponse)
async def get_clean_task(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(CleanTask).filter(
        CleanTask.user_id == current_user.id,
        CleanTask.task_type == "transfer_clean"
    ).first()

    if not task:
        return CleanTaskResponse(
            id=0,
            task_type="transfer_clean",
            last_run=None,
            next_run=None,
            status="not_configured",
            config={}
        )

    return CleanTaskResponse(
        id=task.id,
        task_type=task.task_type,
        last_run=task.last_run,
        next_run=task.next_run,
        status=task.status,
        config=task.get_config()
    )


@router.post("")
async def create_or_update_clean_task(
    config: CleanTaskConfig,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(CleanTask).filter(
        CleanTask.user_id == current_user.id,
        CleanTask.task_type == "transfer_clean"
    ).first()

    if not task:
        task = CleanTask(
            user_id=current_user.id,
            task_type="transfer_clean"
        )
        db.add(task)

    task.set_config(config.model_dump())
    task.status = "scheduled"
    db.commit()

    scheduler = get_task_scheduler(db)
    await scheduler.setup_clean_task(current_user.id, config.model_dump())

    return {"success": True, "message": "Clean task configured"}


@router.post("/{task_id}/run")
async def run_clean_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    task = db.query(CleanTask).filter(
        CleanTask.id == task_id,
        CleanTask.user_id == current_user.id
    ).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    scheduler = get_task_scheduler(db)
    result = await scheduler.execute_clean_now(current_user.id)

    return result


@router.post("/clear-security")
async def clear_security_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    scheduler = get_task_scheduler(db)
    result = await scheduler.clear_security_code(current_user.id)

    if result.get("success"):
        return {"success": True, "message": "Security code cleared"}
    else:
        raise HTTPException(status_code=400, detail=result.get("message", "Failed"))
