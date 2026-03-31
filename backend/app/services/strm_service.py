import os
import re
import aiofiles
from typing import Optional, List
from urllib.parse import quote

from app.core.config import settings
from app.models.media import Media
from app.models.strm_file import STRMFile
from app.models.share_link import ShareLink


class STRMGenerator:
    CATEGORY_PATHS = {
        "movie": "电影",
        "tv": "剧集",
        "anime": "动漫",
        "variety": "综艺"
    }

    def __init__(self, db):
        self.db = db

    async def generate_strm(self, media: Media, episode: int = None) -> str:
        file_url = await self._get_file_url(media)
        
        file_name = self._generate_filename(media, episode)
        category_path = self.CATEGORY_PATHS.get(media.category, "其他")
        relative_path = f"/{category_path}/{file_name}.strm"
        
        strm_content = self._create_strm_content(file_url, media)
        
        save_path = os.path.join(settings.DOWNLOAD_PATH, relative_path.lstrip("/"))
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        async with aiofiles.open(save_path, "w", encoding="utf-8") as f:
            await f.write(strm_content)
        
        strm_record = STRMFile(
            user_id=media.user_id,
            media_id=media.id,
            file_path=relative_path,
            file_url=file_url,
            episode=str(episode) if episode else None
        )
        self.db.add(strm_record)
        self.db.commit()
        
        return relative_path

    async def generate_episodes(self, media: Media) -> List[str]:
        paths = []
        episode_count = media.episode_count or 1
        
        for episode in range(1, episode_count + 1):
            path = await self.generate_strm(media, episode)
            paths.append(path)
        
        return paths

    async def _get_file_url(self, media: Media) -> str:
        if media.share_link_id:
            share_link = self.db.query(ShareLink).filter(
                ShareLink.id == media.share_link_id
            ).first()
            
            if share_link:
                platform = share_link.platform
                
                if platform == "115":
                    return await self._get_115_file_url(share_link)
                elif platform == "baidu":
                    return await self._get_baidu_file_url(share_link)
                elif platform == "aliyun":
                    return await self._get_aliyun_file_url(share_link)
                elif platform == "pikpak":
                    return await self._get_pikpak_file_url(share_link)
        
        return media.file_path or ""

    async def _get_115_file_url(self, share_link: ShareLink) -> str:
        extracted = share_link.get_extracted_info()
        pickcode = extracted.get("pickcode", "")
        share_id = extracted.get("share_id", "")
        
        return f"115://shareid={share_id}&pickcode={pickcode}"

    async def _get_baidu_file_url(self, share_link: ShareLink) -> str:
        extracted = share_link.get_extracted_info()
        surl = extracted.get("surl", "")
        pwd = extracted.get("pwd", "")
        
        return f"baidu://surl={surl}&pwd={pwd}"

    async def _get_aliyun_file_url(self, share_link: ShareLink) -> str:
        extracted = share_link.get_extracted_info()
        shareid = extracted.get("shareid", "")
        itemid = extracted.get("itemid", "")
        
        return f"aliyun://shareid={shareid}&itemid={itemid}"

    async def _get_pikpak_file_url(self, share_link: ShareLink) -> str:
        extracted = share_link.get_extracted_info()
        shareid = extracted.get("shareid", "")
        
        return f"pikpak://shareid={shareid}"

    def _generate_filename(self, media: Media, episode: int = None) -> str:
        title = re.sub(r'[<>:"/\\|?*]', '', media.title or "")
        title_cn = re.sub(r'[<>:"/\\|?*]', '', media.title_cn or title)
        
        if episode:
            season = "S01"
            episode_str = f"E{episode:02d}"
            return f"{title_cn}/{season}{episode_str}"
        
        if media.year:
            return f"{title_cn}/{title_cn}.{media.year}"
        
        return title_cn

    def _create_strm_content(self, file_url: str, media: Media) -> str:
        title = media.title_cn or media.title or "Unknown"
        title = title.replace('"', '\\"')
        
        return f'#EXTM3U\n#EXTINF:-1,{title}\n{file_url}'


class STRMScanner:
    def __init__(self, db):
        self.db = db

    async def scan_directory(self, user_id: int, directory: str) -> List[dict]:
        results = []
        scan_path = os.path.join(settings.DOWNLOAD_PATH, directory.lstrip("/"))
        
        if not os.path.exists(scan_path):
            return results
        
        for root, dirs, files in os.walk(scan_path):
            for file in files:
                if file.endswith(".strm"):
                    file_path = os.path.join(root, file)
                    relative_path = os.path.relpath(file_path, settings.DOWNLOAD_PATH)
                    
                    async with aiofiles.open(file_path, "r", encoding="utf-8") as f:
                        content = await f.read()
                    
                    url = self._extract_url(content)
                    episode = self._extract_episode(file)
                    
                    strm_record = STRMFile(
                        user_id=user_id,
                        file_path="/" + relative_path.replace("\\", "/"),
                        file_url=url,
                        episode=episode
                    )
                    self.db.add(strm_record)
                    
                    results.append({
                        "path": relative_path,
                        "url": url,
                        "episode": episode
                    })
        
        self.db.commit()
        return results

    def _extract_url(self, content: str) -> str:
        lines = content.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                return line
        return ""

    def _extract_episode(self, filename: str) -> Optional[str]:
        match = re.search(r'[ES](\d{2,3})', filename, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
