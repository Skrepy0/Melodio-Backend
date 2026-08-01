from pydantic import BaseModel


class UrlStatus(BaseModel):
    ok: bool  # o不ok
    status_code: int  # 状态码
    reason: list[str]  # 返回信息
