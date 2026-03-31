from abc import ABC, abstractmethod
from typing import Optional
import httpx
import re


class BaseShareParser(ABC):
    platform_name = "unknown"
    
    @abstractmethod
    async def parse(self, url: str) -> dict:
        pass
    
    async def get_download_url(self, url: str, **kwargs) -> str:
        return ""


class BaiduParser(BaseShareParser):
    platform_name = "baidu"
    
    async def parse(self, url: str) -> dict:
        surl_match = re.search(r'surl=([a-zA-Z0-9_-]+)', url)
        pwd_match = re.search(r'pwd=([a-zA-Z0-9]+)', url)
        
        surl = surl_match.group(1) if surl_match else ""
        pwd = pwd_match.group(1) if pwd_match else ""
        
        filename = f"百度网盘分享_{surl}"
        
        return {
            "platform": "baidu",
            "surl": surl,
            "pwd": pwd,
            "filename": filename,
            "title": filename
        }


class AliyunParser(BaseShareParser):
    platform_name = "aliyun"
    
    async def parse(self, url: str) -> dict:
        shareid_match = re.search(r'shareid=([0-9]+)', url)
        itemid_match = re.search(r'itemId=([0-9]+)', url)
        
        shareid = shareid_match.group(1) if shareid_match else ""
        itemid = itemid_match.group(1) if itemid_match else ""
        
        filename = f"阿里云盘分享_{shareid}_{itemid}"
        
        return {
            "platform": "aliyun",
            "shareid": shareid,
            "itemid": itemid,
            "filename": filename,
            "title": filename
        }


class PikPakParser(BaseShareParser):
    platform_name = "pikpak"
    
    async def parse(self, url: str) -> dict:
        shareid_match = re.search(r'share\.pikpak\.com/.*?id=([a-zA-Z0-9_-]+)', url)
        
        shareid = shareid_match.group(1) if shareid_match else ""
        filename = f"PikPak分享_{shareid}"
        
        return {
            "platform": "pikpak",
            "shareid": shareid,
            "filename": filename,
            "title": filename
        }


class One35Parser(BaseShareParser):
    platform_name = "115"
    
    async def parse(self, url: str) -> dict:
        code_match = re.search(r'115\.com/s/([a-zA-Z0-9_-]+)', url)
        
        code = code_match.group(1) if code_match else ""
        filename = f"115分享_{code}"
        
        return {
            "platform": "115",
            "code": code,
            "filename": filename,
            "title": filename
        }


class QuarkParser(BaseShareParser):
    platform_name = "quark"
    
    async def parse(self, url: str) -> dict:
        shareid_match = re.search(r'quark\.cn/s/([a-zA-Z0-9_-]+)', url)
        
        shareid = shareid_match.group(1) if shareid_match else ""
        filename = f"夸克分享_{shareid}"
        
        return {
            "platform": "quark",
            "shareid": shareid,
            "filename": filename,
            "title": filename
        }


class ParserFactory:
    _parsers = {
        "baidu": BaiduParser,
        "aliyun": AliyunParser,
        "pikpak": PikPakParser,
        "115": One35Parser,
        "quark": QuarkParser,
    }
    
    @classmethod
    def get_parser(cls, url: str):
        url_lower = url.lower()
        
        if "baidu.com" in url_lower or "pan.baidu.com" in url_lower:
            return BaiduParser()
        elif "aliyundrive.com" in url_lower or "alipan.com" in url_lower:
            return AliyunParser()
        elif "pikpak.com" in url_lower:
            return PikPakParser()
        elif "115.com" in url_lower:
            return One35Parser()
        elif "quark.cn" in url_lower:
            return QuarkParser()
        elif "xunlei.com" in url_lower:
            return One35Parser()
        
        return None
