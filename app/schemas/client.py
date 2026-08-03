from enum import StrEnum


class MusicClient(StrEnum):
    Bilibili = 'BilibiliMusicClient'
    Bodian = 'BodianMusicClient'
    FiveSing = 'FiveSingMusicClient'
    Kugou = 'KugouMusicClient'
    Kuwo = 'KuwoMusicClient'
    Migu = 'MiguMusicClient'
    MOOV = 'MOOVMusicClient'
    Netease = 'NeteaseMusicClient'
    Qianqian = 'QianqianMusicClient'
    QQ = 'QQMusicClient'
    Soda = 'SodaMusicClient'
    StreetVoice = 'StreetVoiceMusicClient'

    # Apple = "AppleMusicClient"
    # Deezer = "DeezerMusicClient"
    # FMA = "FMAMusicClient"
    # Jamendo = "JamendoMusicClient"
    # Joox = "JooxMusicClient"
    # JioSaavn = "JioSavnMusicClient"
    # OpenGameArt = "OpenGameArtMusicClient"
    # Qobuz = "QobuzMusicClient"
    # SoundCloud = "SoundCloudMusicClient"
    # Spotify = "SpotifyMusicClient"
    # Suno = "SunoMusicClient"
    # TIDAL = "TIDALMusicClient"
    # YouTube = "YouTubeMusicClient"

    @staticmethod
    def is_valid_music_client(value: str) -> bool:
        try:
            MusicClient(value)
            return True
        except ValueError:
            return False
