class InvalidMusicClientError(ValueError):
    def __init__(self, code: int, client_name: str):
        self.code = code
        self.client_name = client_name
        super().__init__(f"music_client '{client_name}' 不合法")
