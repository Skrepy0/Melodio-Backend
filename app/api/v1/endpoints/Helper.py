from typing import List, Dict, Tuple, Callable, Any

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


class NotifyList(list):
    """监听列表添加操作的自定义列表"""

    def __init__(self, on_add: Callable[[Any], None], iterable=None):
        super().__init__(iterable or [])
        self.on_add = on_add

    def append(self, item):
        super().append(item)
        self.on_add(item)

    def extend(self, iterable):
        super().extend(iterable)
        for item in iterable:
            self.on_add(item)


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


def _search_source_with_callbacks(
    source: str, keyword: str, limit: int, on_song: Callable[[SongInfo], None]
) -> None:
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

        # 创建带回调的 bucket
        bucket = NotifyList(on_add=on_song)

        search_urls = real_client._constructsearchurls(
            keyword=keyword, rule={}, request_overrides={}
        )
        if not search_urls:
            return

        for url in search_urls:
            real_client._search(
                keyword=keyword,
                search_url=url,
                request_overrides={},
                song_infos=bucket,
                progress=progress,
            )
    except Exception as e:
        print(f'[ERROR] Source {source} failed: {e}')
