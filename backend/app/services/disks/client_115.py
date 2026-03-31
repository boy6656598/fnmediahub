import httpx
import time
import uuid
from typing import Optional, Dict
from urllib.parse import urlencode


class Client115:
    BASE_URL = "https://webapi.115.com"
    PASSPORT_URL = "https://passport.115.com"

    def __init__(self):
        self.uid: Optional[str] = None
        self.token: Optional[str] = None
        self.timezone: Optional[str] = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

    async def get_qrcode(self) -> Dict:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            device_id = str(uuid.uuid4())
            params = {
                "app": "115",
                "device_id": device_id,
                "device_token": device_id,
                " scan_time": int(time.time())
            }
            response = await client.get(
                f"{self.PASSPORT_URL}/qr/2020/getdata",
                params=params
            )
            data = response.json()
            
            if data.get("state"):
                return {
                    "uuid": data.get("uid"),
                    "qrcode_url": data.get("qrcode"),
                    "expires_in": 300
                }
            raise Exception(f"获取二维码失败: {data.get('error')}")

    async def check_qrcode_status(self, uuid: str) -> Dict:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            params = {"uid": uuid, "_": int(time.time() * 1000)}
            response = await client.get(
                f"{self.PASSPORT_URL}/qr/2020/check",
                params=params
            )
            data = response.json()
            
            status_map = {
                "-1": "expired",
                "0": "waiting",
                "1": "scanned",
                "2": "confirmed"
            }
            
            status = status_map.get(str(data.get("state")), "unknown")
            result = {"status": status}
            
            if status == "confirmed":
                result["uid"] = data.get("uid")
                result["token"] = data.get("token")
                self.uid = data.get("uid")
                self.token = data.get("token")
            
            return result

    async def login_with_token(self, uid: str, token: str) -> bool:
        self.uid = uid
        self.token = token
        
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            params = {"uid": uid, "token": token}
            response = await client.get(
                f"{self.BASE_URL}/user/check_signin",
                params=params
            )
            data = response.json()
            return data.get("state") == True

    async def get_file_list(self, path: str = "/", page: int = 1) -> Dict:
        if not self.uid or not self.token:
            raise Exception("未登录115网盘")

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            params = {
                "aid": 1,
                "cid": 0,
                "offset": (page - 1) * 100,
                "limit": 100,
                "show_dir": 1,
                "asc": 0,
                "order": "file_name"
            }
            response = await client.get(
                f"{self.BASE_URL}/files",
                params=params
            )
            data = response.json()
            
            if data.get("state"):
                return {
                    "files": data.get("data", []),
                    "count": data.get("count", 0),
                    "page": page
                }
            raise Exception(f"获取文件列表失败: {data.get('error')}")

    async def get_share_info(self, share_url: str) -> Dict:
        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.get(share_url)
            html = response.text
            
            import re
            match = re.search(r'"pickcode":\s*"([^"]+)"', html)
            pickcode = match.group(1) if match else ""
            
            match = re.search(r'"share_id":\s*(\d+)', html)
            share_id = match.group(1) if match else ""
            
            return {
                "pickcode": pickcode,
                "share_id": share_id,
                "url": share_url
            }

    async def get_share_file_list(self, share_id: str, pickcode: str) -> Dict:
        if not self.uid or not self.token:
            raise Exception("未登录115网盘")

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            params = {
                "share_id": share_id,
                "pickcode": pickcode,
                "aid": 1,
                "offset": 0,
                "limit": 100
            }
            response = await client.get(
                f"{self.BASE_URL}/share/sharelink，翻页",
                params=params
            )
            data = response.json()
            
            if data.get("state"):
                return {
                    "files": data.get("data", []),
                    "count": data.get("count", 0)
                }
            raise Exception(f"获取分享文件列表失败: {data.get('error')}")

    async def clear_security(self) -> Dict:
        if not self.uid or not self.token:
            raise Exception("未登录115网盘")

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            response = await client.post(
                f"{self.BASE_URL}/files/security",
                data={"verify_type": 1}
            )
            data = response.json()
            return {"success": data.get("state", False), "message": data.get("message", "")}

    async def get_user_info(self) -> Dict:
        if not self.uid or not self.token:
            raise Exception("未登录115网盘")

        async with httpx.AsyncClient(headers=self.headers, timeout=30) as client:
            params = {"uid": self.uid}
            response = await client.get(
                f"{self.BASE_URL}/user/info",
                params=params
            )
            data = response.json()
            
            if data.get("state"):
                return {
                    "uid": data.get("uid"),
                    "user_name": data.get("user_name"),
                    "storage_total": data.get("storage", {}).get("total", 0),
                    "storage_used": data.get("storage", {}).get("used", 0)
                }
            raise Exception(f"获取用户信息失败: {data.get('error')}")

    def is_logged_in(self) -> bool:
        return bool(self.uid and self.token)
