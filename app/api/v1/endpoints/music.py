import asyncio
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple, List, Dict

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


class _NullProgress:
    def add_task(self, *a, **k):
        return 0

    def update(self, *a, **k):
        pass

    def advance(self, *a, **k):
        pass

    def __getattr__(self, _):
        return lambda *a, **k: None


@router.get(
    '/search',
    response_model=SongResponse,
    summary='搜索歌曲',
    description='并发搜索多个音乐源，支持超时后返回部分结果',
)
async def search_songs(
    keyword: str = Query(
        ..., min_length=1, max_length=100, description='搜索关键词'
    ),
    music_client: list[str] = Query(
        [MusicClient.Bilibili], description='搜索音乐源'
    ),
    limit: int = Query(10, ge=1, le=50, description='每个源的返回条数'),
    timeout: int = Query(40, ge=1, le=600, description='最大搜索时间'),
    _: bool = Depends(verify_signature),
):
    for client in music_client:
        if not MusicClient.is_valid_music_client(client):
            raise InvalidMusicClientError(code=1001, client_name=client)

    def search_source(source: str, bucket: List[Dict]) -> Tuple[str, bool]:
        try:
            cfg = {
                source: {
                    'search_size_per_source': limit,
                    'work_dir': f'/tmp/musicdl_outputs/{source}',
                }
            }
            cli = musicdl.MusicClient(
                music_sources=[source],
                init_music_clients_cfg=cfg,
            )
            real_client = cli.music_clients[source]
            progress = _NullProgress()

            search_urls = real_client._constructsearchurls(
                keyword=keyword, rule={}, request_overrides={}
            )
            if not search_urls:
                return source, False

            for url in search_urls:
                real_client._search(
                    keyword=keyword,
                    search_url=url,
                    request_overrides={},
                    song_infos=bucket,
                    progress=progress,
                )
            return source, False
        except Exception as e:
            print(f'[ERROR] Source {source} failed: {e}')
            return source, False

    buckets = {source: [] for source in music_client}
    executor = ThreadPoolExecutor(max_workers=len(music_client))
    loop = asyncio.get_running_loop()

    futures = []
    for source in music_client:
        future = loop.run_in_executor(
            executor, search_source, source, buckets[source]
        )
        futures.append(future)

    start_time = time.time()
    completed_sources = set()
    timeout_sources = []

    while (
        len(completed_sources) < len(music_client)
        and (time.time() - start_time) < timeout
    ):
        for i, fut in enumerate(futures):
            if fut.done() and i not in completed_sources:
                try:
                    fut.result()
                    completed_sources.add(i)
                except Exception:
                    completed_sources.add(i)
        await asyncio.sleep(0.1)

    if len(completed_sources) < len(music_client):
        for i, fut in enumerate(futures):
            if not fut.done():
                fut.cancel()
                timeout_sources.append(music_client[i])

    combined = {}
    for source, bucket in buckets.items():
        if bucket:
            combined[source] = bucket

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
