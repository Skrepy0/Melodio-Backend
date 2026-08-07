import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends, Query
from musicdl import musicdl
from starlette.responses import StreamingResponse

from app.api.v1.endpoints.Helper import (
    format_song_data,
    format_parse_list_data,
    _search_source,
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

    buckets = {source: [] for source in music_client}
    executor = ThreadPoolExecutor(max_workers=len(music_client))
    loop = asyncio.get_running_loop()

    futures = []
    for source in music_client:
        future = loop.run_in_executor(
            executor, _search_source, source, keyword, limit, buckets[source]
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
    '/search_stream',
    summary='搜索歌曲（SSE）',
    description='并发搜索多个音乐源，每个源完成时立即通过 SSE 推送结果，支持超时后返回部分结果',
)
async def search_stream(
    keyword: str = Query(
        ..., min_length=1, max_length=100, description='搜索关键词'
    ),
    music_client: list[str] = Query(
        [MusicClient.Bilibili], description='搜索音乐源'
    ),
    limit: int = Query(10, ge=1, le=50, description='每个源的返回条数'),
    timeout: int = Query(40, ge=1, le=600, description='最大搜索时间（秒）'),
    _: bool = Depends(verify_signature),
):
    for client in music_client:
        if not MusicClient.is_valid_music_client(client):
            raise InvalidMusicClientError(code=1001, client_name=client)

    async def event_generator():
        """
        异步生成器，产出 SSE 格式的数据流。
        """
        loop = asyncio.get_running_loop()
        # 每个源一个独立的 bucket
        buckets = {source: [] for source in music_client}
        # 使用线程池并发执行搜索
        executor = ThreadPoolExecutor(max_workers=len(music_client))
        future_to_source = {}

        # 提交所有搜索任务
        for source in music_client:
            future = loop.run_in_executor(
                executor,
                _search_source,
                source,
                keyword,
                limit,
                buckets[source],
            )
            future_to_source[future] = source

        pending = set(future_to_source.keys())
        start_time = time.time()

        # 循环等待任务完成，直到所有任务完成或超时
        while pending and (time.time() - start_time) < timeout:
            # 每次等待最多 1 秒，以便及时检查总超时
            done, pending = await asyncio.wait(
                pending, timeout=1, return_when=asyncio.FIRST_COMPLETED
            )
            for fut in done:
                source = future_to_source[fut]
                try:
                    # 重新抛出任务中可能的异常
                    await fut
                    # 如果该源有搜索结果，立即推送
                    if buckets[source]:
                        items = format_song_data({source: buckets[source]})
                        serializable_items = [
                            item.model_dump()
                            if hasattr(item, 'model_dump')
                            else item.dict()
                            for item in items
                        ]
                        data = {
                            'source': source,
                            'items': serializable_items,
                            'status': 'partial',
                        }
                        yield f'data: {json.dumps(data, ensure_ascii=False)}\n\n'
                except Exception as e:
                    # 单个源失败，不中断整体流程
                    print(f'Source {source} failed: {e}')

        # 超时或所有任务完成，取消尚未完成的任务
        for fut in pending:
            fut.cancel()
        executor.shutdown(wait=False)

        # 发送结束信号
        yield f'data: {json.dumps({"status": "done"})}\n\n'

    # 返回 SSE 流式响应
    return StreamingResponse(event_generator(), media_type='text/event-stream')


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
