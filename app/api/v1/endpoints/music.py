from fastapi import APIRouter, Depends, Query, HTTPException

from app.schemas.client import MusicClient
from app.schemas.music import SongResponse
from app.core.dependencies import verify_signature
from app.utils.exceptions import InvalidMusicClientError

router = APIRouter()


@router.get(
    '/search',
    response_model=SongResponse,
    summary='搜索歌曲',
    description='根据关键词搜索歌曲',
)
async def search_songs(
    # Query 参数
    keyword: str = Query(
        ..., min_length=1, max_length=100, description='搜索关键词'
    ),
    music_client: list[str] = Query(
        [MusicClient.Bilibili], description='音乐来源'
    ),
    limit: int = Query(10, ge=1, le=50, description='返回条数，最大 50'),
    # 签名校验
    _: bool = Depends(verify_signature),
):
    # 检查music_client是否合法
    for client in music_client:
        if not MusicClient.is_valid_music_client(client):
            raise InvalidMusicClientError(code=1001, client_name=client)
    # TODO
    return SongResponse(total=0, items=[])
