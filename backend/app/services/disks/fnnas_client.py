import httpx
from typing import List, Optional


class FnNASClient:
    def __init__(self, host: str, token: str = ""):
        self.host = host.rstrip("/")
        self.token = token
        self.session = None
    
    async def login(self) -> bool:
        if not self.token:
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.host}/api/system/login/check",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=10
                )
                return response.status_code == 200
        except Exception:
            return False
    
    async def list_files(self, path: str = "/") -> List[dict]:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.host}/api/file/list",
                    params={"path": path},
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=10
                )
                if response.status_code == 200:
                    data = response.json()
                    return data.get("data", []).get("files", [])
        except Exception:
            pass
        return []
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                with open(local_path, "rb") as f:
                    files = {"file": f}
                    data = {"path": remote_path}
                    response = await client.post(
                        f"{self.host}/api/file/upload",
                        files=files,
                        data=data,
                        headers={"Authorization": f"Bearer {self.token}"},
                        timeout=60
                    )
                    return response.status_code == 200
        except Exception:
            return False
    
    async def get_file_url(self, file_path: str) -> str:
        return f"{self.host}/api/file/stream?path={file_path}"
    
    async def get_storage_info(self) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.host}/api/system/storage",
                    headers={"Authorization": f"Bearer {self.token}"},
                    timeout=10
                )
                if response.status_code == 200:
                    return response.json()
        except Exception:
            pass
        return {"total": 0, "used": 0}
