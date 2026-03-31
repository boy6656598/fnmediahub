import httpx
from typing import List
from urllib.parse import urljoin


class WebDAVClient:
    def __init__(self, host: str, username: str = "", password: str = ""):
        self.host = host.rstrip("/")
        self.username = username
        self.password = password
        self.session = None
    
    async def list_files(self, path: str = "/") -> List[dict]:
        propfind_body = """<?xml version="1.0" encoding="utf-8"?>
        <propfind xmlns="DAV:">
            <prop>
                <displayname/>
                <getcontentlength/>
                <getlastmodified/>
                <resourcetype/>
            </prop>
        </propfind>"""
        
        try:
            async with httpx.AsyncClient(auth=(self.username, self.password)) as client:
                response = await client.request(
                    "PROPFIND",
                    urljoin(self.host, path),
                    content=propfind_body.encode(),
                    headers={"Depth": "1"},
                    timeout=10
                )
                if response.status_code in (207, 200):
                    return self._parse_propfind_response(response.text)
        except Exception:
            pass
        return []
    
    def _parse_propfind_response(self, xml_content: str) -> List[dict]:
        import re
        files = []
        
        href_pattern = r'<d:href>([^<]+)</d:href>'
        displayname_pattern = r'<d:displayname>([^<]*)</d:displayname>'
        contentlength_pattern = r'<d:getcontentlength>([^<]*)</d:getcontentlength>'
        restype_pattern = r'<d:resourcetype><d:collection/></d:resourcetype>'
        
        hrefs = re.findall(href_pattern, xml_content)
        
        for href in hrefs:
            displayname = re.search(displayname_pattern, xml_content.split(href)[1] if href in xml_content else "")
            contentlength = re.search(contentlength_pattern, xml_content.split(href)[1] if href in xml_content else "")
            is_dir = bool(re.search(restype_pattern, xml_content.split(href)[1] if href in xml_content else ""))
            
            files.append({
                "name": displayname.group(1) if displayname else href.split("/")[-1],
                "path": href,
                "size": int(contentlength.group(1)) if contentlength and contentlength.group(1) else 0,
                "is_dir": is_dir
            })
        
        return [f for f in files if f["name"]]
    
    async def upload_file(self, local_path: str, remote_path: str) -> bool:
        try:
            with open(local_path, "rb") as f:
                content = f.read()
            
            async with httpx.AsyncClient(auth=(self.username, self.password)) as client:
                response = await client.put(
                    urljoin(self.host, remote_path),
                    content=content,
                    timeout=60
                )
                return response.status_code in (200, 201, 204)
        except Exception:
            return False
    
    async def get_file_url(self, file_path: str) -> str:
        return urljoin(self.host, file_path)
    
    async def download_file(self, remote_path: str, local_path: str) -> bool:
        try:
            async with httpx.AsyncClient(auth=(self.username, self.password)) as client:
                response = await client.get(
                    urljoin(self.host, remote_path),
                    timeout=60
                )
                if response.status_code == 200:
                    with open(local_path, "wb") as f:
                        f.write(response.content)
                    return True
        except Exception:
            pass
        return False
