from fastapi import APIRouter, Depends, Query, HTTPException
from musicdl import musicdl

from app.schemas.client import MusicClient
from app.schemas.music import SongResponse, SongItem
from app.core.dependencies import verify_signature
from app.schemas.url_status import UrlStatus
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
    results: list[SongItem] = []
    for client in search_results:
        for song_info in search_results[client]:
            results.append(
                SongItem(
                    source=song_info.source,
                    name=song_info.song_name,
                    singers=song_info.singers,
                    album=song_info.album,
                    ext=song_info.ext,
                    file_size_bytes=song_info.file_size_bytes,
                    duration=song_info.duration_s,
                    lyric=song_info.lyric,
                    cover_url=song_info.cover_url,
                    download_url=song_info.download_url,
                    download_url_status=UrlStatus(
                        ok=song_info.download_url_status['ok'],
                        status_code=song_info.download_url_status[
                            'status_code'
                        ],
                        reason=song_info.download_url_status['reason'],
                    ),
                    identifier=song_info.identifier,
                )
            )
    return SongResponse(total=len(results), items=results)
