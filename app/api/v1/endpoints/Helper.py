from typing import List, Dict, Tuple

from musicdl import musicdl
from musicdl.modules import SongInfo

from app.schemas.music import SongItem
from app.schemas.url_status import UrlStatus


def format_song_data(
    search_results: dict[str, list[SongInfo]],
) -> list[SongItem]:
    results: list[SongItem] = []
    for client in search_results:
        results += format_parse_list_data(search_results[client])
    return results


def format_parse_list_data(search_results: list[SongInfo]) -> list[SongItem]:
    results: list[SongItem] = []
    for song_info in search_results:
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
                    status_code=song_info.download_url_status['status_code'],
                    reason=song_info.download_url_status['reason'],
                ),
                identifier=song_info.identifier,
            )
        )
    return results


class _NullProgress:
    def add_task(self, *a, **k):
        return 0

    def update(self, *a, **k):
        pass

    def advance(self, *a, **k):
        pass

    def __getattr__(self, _):
        return lambda *a, **k: None


def _search_source(
    source: str, keyword: str, limit: int, bucket: List[Dict]
) -> Tuple[str, bool]:
    """
    在单个音乐源上执行搜索，结果追加到 bucket 中。
    返回 (source, success) 标记是否成功。
    """
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
        return source, True
    except Exception as e:
        print(f'[ERROR] Source {source} failed: {e}')
        return source, False
