from fastapi import APIRouter, Depends, Query
from musicdl import musicdl

from app.api.v1.endpoints.Helper import (
    format_song_data,
    format_parse_list_data,
)
from app.schemas.client import MusicClient
from app.schemas.music import SongResponse
from app.core.dependencies import verify_signature
from app.utils.exceptions import (
    InvalidMusicClientError,
    ArrayLengthMismatchError,
)

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
    limit: int = Query(
        10, ge=1, le=50, description='每个源的返回条数，最大 50'
    ),
    # 签名校验
    _: bool = Depends(verify_signature),
):
    # 检查music_client是否合法
    init_music_clients_cfg = {}
    for client in music_client:
        if not MusicClient.is_valid_music_client(client):
            raise InvalidMusicClientError(code=1001, client_name=client)
        else:
            init_music_clients_cfg[client] = {'search_size_per_source': limit}
    musicClient = musicdl.MusicClient(
        music_sources=music_client,
        init_music_clients_cfg=init_music_clients_cfg,
    )
    search_results = musicClient.search(keyword=keyword)
    results = format_song_data(search_results)
    return SongResponse(total=len(results), items=results)


@router.get(
    '/parse_song_list',
    response_model=SongResponse,
    summary='解析歌单',
    description='根据链接解析歌单',
)
async def parse_song_list(
    music_client: list[str] = Query(
        [MusicClient.Bilibili], description='音乐来源'
    ),
    url: str = Query('', description='歌单地址'),
    limit: int = Query(
        10, ge=1, le=50, description='每个源的返回条数，最大 50'
    ),
    _: bool = Depends(verify_signature),
):
    if not len(music_client) == 1:
        raise ArrayLengthMismatchError(
            code=1002,
            expected=1,
            actual=len(music_client),
            array_name='music_client',
        )
    client = music_client[0]
    init_music_clients_cfg = {}
    if not MusicClient.is_valid_music_client(client):
        raise InvalidMusicClientError(code=1001, client_name=client)
    else:
        init_music_clients_cfg[client] = {'search_size_per_source': limit}
    musicClient = musicdl.MusicClient(
        music_sources=music_client,
        init_music_clients_cfg=init_music_clients_cfg,
    )
    parse_results = musicClient.parseplaylist(url)
    results = format_parse_list_data(parse_results)
    return SongResponse(total=len(results), items=results)
