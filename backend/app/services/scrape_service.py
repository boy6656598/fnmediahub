import re
import httpx
from typing import Optional


class ScrapeService:
    def __init__(self):
        self.tmdb_api_key = None
        self.douban_api_key = None
    
    async def scrape_from_filename(self, filename: str) -> dict:
        info = self._extract_media_info(filename)
        
        title = info.get("title", filename)
        year = info.get("year")
        media_type = info.get("media_type", "movie")
        
        tmdb_result = await self._search_tmdb(title, year, media_type)
        
        if tmdb_result:
            result = tmdb_result
            if not result.get("title_cn") and result.get("title"):
                douban_result = await self._search_douban(title, media_type)
                if douban_result:
                    result["title_cn"] = douban_result.get("title_cn")
                    result["overview"] = douban_result.get("overview") or result.get("overview")
        else:
            result = {
                "title": filename,
                "title_cn": None,
                "media_type": media_type,
                "year": year,
                "poster_url": None,
                "backdrop_url": None,
                "overview": None,
                "tmdb_id": None
            }
        
        return result
    
    def _extract_media_info(self, filename: str) -> dict:
        filename = re.sub(r'[\[\(].*?[\]\)]', ' ', filename)
        filename = re.sub(r'\.(mp4|mkv|avi|mov|wmv|flv|webm|m4v)$', '', filename, flags=re.IGNORECASE)
        filename = filename.strip()
        
        year_match = re.search(r'(19|20)\d{2}', filename)
        year = int(year_match.group()) if year_match else None
        
        if re.search(r'S\d+E\d+', filename, re.IGNORECASE):
            media_type = "tv"
        elif re.search(r'第\d+季|第\d+辑', filename):
            media_type = "tv"
        else:
            media_type = "movie"
        
        title = re.sub(r'(19|20)\d{2}[.\s-]*', '', filename)
        title = re.sub(r'[Ss]\d+[Ee]\d+.*$', '', title)
        title = re.sub(r'第\d+季.*$', '', title)
        title = re.sub(r'[.\s-]*(720p|1080p|2160p|4k|hr|bluray|webrip|dvdrip|hdrip|brrip|蓝光|高清|超清|完结|连载).*$', '', title, flags=re.IGNORECASE)
        title = title.strip('. ')
        
        return {
            "title": title or filename,
            "year": year,
            "media_type": media_type
        }
    
    async def _search_tmdb(self, title: str, year: Optional[int], media_type: str) -> Optional[dict]:
        try:
            url = f"https://api.themoviedb.org/3/search/{media_type}"
            params = {"query": title, "api_key": self.tmdb_api_key}
            if year:
                params["primary_release_year"] = year
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    results = data.get("results", [])
                    if results:
                        item = results[0]
                        return {
                            "title": item.get("title") or item.get("name"),
                            "title_cn": None,
                            "poster_url": f"https://image.tmdb.org/t/p/w500{item.get('poster_path')}" if item.get("poster_path") else None,
                            "backdrop_url": f"https://image.tmdb.org/t/p/original{item.get('backdrop_path')}" if item.get("backdrop_path") else None,
                            "media_type": media_type,
                            "year": item.get("release_date", "")[:4] if item.get("release_date") else year,
                            "overview": item.get("overview"),
                            "tmdb_id": str(item.get("id"))
                        }
        except Exception:
            pass
        
        return None
    
    async def _search_douban(self, title: str, media_type: str) -> Optional[dict]:
        try:
            url = "https://www.douban.com/search"
            params = {"q": title, "cat": "1002" if media_type == "movie" else "1003"}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    pass
        except Exception:
            pass
        
        return None
    
    async def search_tmdb(self, keyword: str, media_type: str = "movie") -> list:
        try:
            url = f"https://api.themoviedb.org/3/search/{media_type}"
            params = {"query": keyword, "api_key": self.tmdb_api_key}
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("results", [])
        except Exception:
            pass
        
        return []
