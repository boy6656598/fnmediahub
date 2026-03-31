from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.models.user import User

router = APIRouter()


class UserCreate(BaseModel):
    username: str
    password: str
    disk_type: str = "fnnas"
    disk_config: dict = None


class UserResponse(BaseModel):
    id: int
    username: str
    disk_type: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    username: str
    password: str
    disk_type: str = "fnnas"
    disk_config: dict = None


@router.post("/login", response_model=Token)
async def login(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == login_data.username).first()
    
    if not user:
        user = User(
            username=login_data.username,
            password_hash=get_password_hash(login_data.password),
            disk_type=login_data.disk_type
        )
        if login_data.disk_config:
            user.set_disk_config(login_data.disk_config)
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    else:
        if login_data.disk_config and login_data.disk_config != user.get_disk_config():
            user.set_disk_config(login_data.disk_config)
            db.commit()

    access_token = create_access_token(
        data={"sub": user.id},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.put("/password")
async def change_password(
    old_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not verify_password(old_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Old password is incorrect"
        )
    current_user.password_hash = get_password_hash(new_password)
    db.commit()
    return {"message": "Password updated successfully"}


@router.get("/disk-status")
async def get_disk_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    disk_config = current_user.get_disk_config()
    return {
        "disk_type": current_user.disk_type,
        "disk_config": disk_config,
        "connected": bool(disk_config.get("host") if current_user.disk_type == "webdav" else disk_config.get("token"))
    }
