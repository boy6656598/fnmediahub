from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.services.disks.client_115 import Client115

router = APIRouter()

_115_clients = {}


class QRCodeResponse(BaseModel):
    uuid: str
    qrcode_url: str
    expires_in: int


class QRCodeStatusResponse(BaseModel):
    status: str
    uid: Optional[str] = None
    token: Optional[str] = None


@router.post("/115/qrcode", response_model=QRCodeResponse)
async def get_115_qrcode(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = Client115()

    try:
        result = await client.get_qrcode()
        _115_clients[current_user.id] = client

        return QRCodeResponse(
            uuid=result["uuid"],
            qrcode_url=result["qrcode_url"],
            expires_in=result["expires_in"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Get QRCode failed: {str(e)}")


@router.get("/115/qrcode/{uuid}", response_model=QRCodeStatusResponse)
async def check_115_qrcode(
    uuid: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    client = _115_clients.get(current_user.id)
    if not client:
        raise HTTPException(status_code=400, detail="No QRCode requested")

    try:
        result = await client.check_qrcode_status(uuid)

        if result["status"] == "confirmed":
            uid = result["uid"]
            token = result["token"]

            await client.login_with_token(uid, token)
            user_info = await client.get_user_info()

            disk_config = {
                "uid": uid,
                "token": token,
                "user_name": user_info.get("user_name"),
                "storage_total": user_info.get("storage_total"),
                "storage_used": user_info.get("storage_used")
            }

            current_user.disk_type = "115"
            current_user.set_disk_config(disk_config)
            db.commit()

            _115_clients[current_user.id] = client

            return QRCodeStatusResponse(
                status="confirmed",
                uid=uid,
                token=token
            )

        return QRCodeStatusResponse(status=result["status"])

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check QRCode failed: {str(e)}")


@router.post("/115/logout")
async def logout_115(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.id in _115_clients:
        del _115_clients[current_user.id]

    disk_config = current_user.get_disk_config()
    disk_config.pop("uid", None)
    disk_config.pop("token", None)
    current_user.set_disk_config(disk_config)
    db.commit()

    return {"success": True}


@router.get("/115/status")
async def get_115_status(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    disk_config = current_user.get_disk_config()

    if not disk_config.get("uid") or not disk_config.get("token"):
        return {"logged_in": False}

    client = Client115()
    try:
        logged_in = await client.login_with_token(
            disk_config["uid"],
            disk_config["token"]
        )
        return {
            "logged_in": logged_in,
            "user_name": disk_config.get("user_name"),
            "storage_total": disk_config.get("storage_total"),
            "storage_used": disk_config.get("storage_used")
        }
    except:
        return {"logged_in": False}
