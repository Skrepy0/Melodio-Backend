class InvalidMusicClientError(ValueError):
    def __init__(self, code: int, client_name: str):
        self.code = code
        self.client_name = client_name
        super().__init__(f"music_client '{client_name}' 不合法")


class ArrayLengthMismatchError(Exception):
    """当数组长度不符合预期时抛出"""

    def __init__(
        self, code: int, expected: int, actual: int, array_name: str = 'array'
    ):
        self.code = code
        self.expected = expected
        self.actual = actual
        self.array_name = array_name
        super().__init__(f'{array_name} 长度应为 {expected}，实际为 {actual}')
