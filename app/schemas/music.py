from typing import Optional, List

from pydantic import BaseModel

from app.schemas.url_status import UrlStatus


class SearchQuery(BaseModel):
    keyword: str
    limit: Optional[int] = 10


class SongItem(BaseModel):
    source: str  # 歌曲来源
    name: str  # 曲名
    singers: str  # 歌手
    album: str  # 专辑
    ext: str  # 扩展名,如flac,mp3
    file_size_bytes: int  # 文件大小
    duration: float  # 时长
    lyric: str | None  # 歌词
    cover_url: str | None  # 封面图片地址
    download_url: str | None  # 下载地址
    download_url_status: UrlStatus | None  # 下载地址状态
    identifier: str | int  # id


class SongResponse(BaseModel):
    total: int
    items: List[SongItem]
