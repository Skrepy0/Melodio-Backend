from enum import StrEnum


class MusicClient(StrEnum):
    Bilibili = 'BilibiliMusicClient'
    Bodian = 'BodianMusicClient'
    Kugou = 'KugouMusicClient'
    Kuwo = 'KuwoMusicClient'
    Migu = 'MiguMusicClient'
    Netease = 'NeteaseMusicClient'
    Qianqian = 'QianqianMusicClient'
    QQ = 'QQMusicClient'
    Apple = 'AppleMusicClient'
    Joox = 'JooxMusicClient'
    Qobuz = 'QobuzMusicClient'
    Suno = 'SunoMusicClient'
    MyFreeMP3 = 'MyFreeMP3MusicClient'
    TuneHub = 'TuneHubMusicClient'
    XiaoBai = 'XiaoBaiMusicClient'
    Fangpi = 'FangpiMusicClient'
    Gequbao = 'GequbaoMusicClient'
    Gequhai = 'GequhaiMusicClient'
    Mitu = 'MituMusicClient'
    Zhuolin = 'ZhuolinMusicClient'
    TwoT58 = 'TwoT58MusicClient'

    @staticmethod
    def is_valid_music_client(value: str) -> bool:
        try:
            MusicClient(value)
            return True
        except ValueError:
            return False
