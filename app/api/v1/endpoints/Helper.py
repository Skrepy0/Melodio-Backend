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
