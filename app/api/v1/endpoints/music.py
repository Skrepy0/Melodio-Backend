import asyncio
from typing import Tuple

from fastapi import APIRouter, Depends, Query
from musicdl import musicdl

from app.api.v1.endpoints.Helper import (
    format_song_data,
    format_parse_list_data,
)
from app.core.dependencies import verify_signature
from app.schemas.client import MusicClient
from app.schemas.music import SongResponse
from app.utils.exceptions import (
    InvalidMusicClientError,
    ArrayLengthMismatchError,
)

router = APIRouter()


@router.get(
    '/search',
    response_model=SongResponse,
    summary='搜索歌曲',
    description='根据关键词并发搜索多个音乐源',
)
async def search_songs(
    keyword: str = Query(
        ..., min_length=1, max_length=100, description='搜索关键词'
    ),
    music_client: list[str] = Query(
        [MusicClient.Bilibili], description='音乐来源列表'
    ),
    limit: int = Query(
        10, ge=1, le=50, description='每个源的返回条数，最大 50'
    ),
    _: bool = Depends(verify_signature),
):
    for client in music_client:
        if not MusicClient.is_valid_music_client(client):
            raise InvalidMusicClientError(code=1001, client_name=client)
    PER_SOURCE_TIMEOUT = min(10 * limit, 40)

    async def search_single_source(source: str) -> Tuple[str, dict, bool]:
        cfg = {
            source: {
                'search_size_per_source': limit,
                'work_dir': f'/tmp/musicdl_outputs/{source}',
            }
        }
        try:
            cli = musicdl.MusicClient(
                music_sources=[source],
                init_music_clients_cfg=cfg,
            )
            res = await asyncio.wait_for(
                asyncio.to_thread(cli.search, keyword),
                timeout=PER_SOURCE_TIMEOUT,
            )
            return source, res, False
        except asyncio.TimeoutError:
            print(
                f'[TIMEOUT] Source {source} exceeded {PER_SOURCE_TIMEOUT}s, discarded.'
            )
            return source, {source: []}, True
        except Exception as e:
            print(f'[ERROR] Source {source} failed: {e}')
            return source, {source: []}, False

    tasks = [search_single_source(source) for source in music_client]
    results = await asyncio.gather(*tasks)

    combined = {}
    timeout_sources = []

    for source_name, result, is_timeout in results:
        if is_timeout:
            timeout_sources.append(source_name)
        else:
            combined.update(result)

    items = format_song_data(combined)

    return SongResponse(
        total=len(items),
        items=items,
    )


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
        init_music_clients_cfg[client] = {
            'search_size_per_source': limit,
            'work_dir': f'/tmp/musicdl_outputs/{client}',
        }
    musicClient = musicdl.MusicClient(
        music_sources=music_client,
        init_music_clients_cfg=init_music_clients_cfg,
    )
    parse_results = musicClient.parseplaylist(url)
    results = format_parse_list_data(parse_results)
    return SongResponse(total=len(results), items=results)
