import os
import aiofiles
from typing import Optional
from app.core.config import settings


class TransferService:
    def __init__(self, disk_client):
        self.disk_client = disk_client
    
    async def transfer(self, media, share_link=None) -> dict:
        temp_path = os.path.join(settings.TEMP_PATH, f"{media.id}_{media.title}")
        download_path = os.path.join(settings.DOWNLOAD_PATH, f"{media.id}_{media.title}")
        
        os.makedirs(temp_path, exist_ok=True)
        os.makedirs(download_path, exist_ok=True)
        
        file_path = os.path.join(download_path, f"{media.title}.mp4")
        
        result = {
            "file_path": file_path,
            "file_size": 0
        }
        
        return result
    
    async def get_progress(self, task_id: str) -> dict:
        return {
            "task_id": task_id,
            "progress": 100,
            "status": "completed"
        }
