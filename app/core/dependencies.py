import hashlib
import hmac
import time

from slowapi import Limiter
from fastapi import Request, HTTPException
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=['100/day'])


def verify_signature(request: Request):
    timestamp = request.headers.get('X-Timestamp')
    nonce = request.headers.get('X-Nonce')
    signature = request.headers.get('X-Signature')

    if not all([timestamp, nonce, signature]):
        raise HTTPException(
            status_code=403,
            detail='Missing signature headers (X-Timestamp, X-Nonce, X-Signature)',
        )

    try:
        req_time = int(timestamp)
    except ValueError:
        raise HTTPException(status_code=403, detail='Invalid timestamp format')

    now = int(time.time())
    expire_seconds = getattr(
        settings, 'SIGNATURE_EXPIRE_SECONDS', 300
    )  # 默认5分钟
    if abs(now - req_time) > expire_seconds:
        raise HTTPException(status_code=403, detail='Request expired')

    method = request.method
    path = request.url.path

    query_params = sorted(request.query_params.items())
    query_str = '&'.join([f'{k}={v}' for k, v in query_params])

    sign_str = f'{method}&{path}&{query_str}&{timestamp}&{nonce}'

    secret_key = getattr(settings, 'SECRET_KEY', None)
    if not secret_key:
        raise HTTPException(
            status_code=500,
            detail='Server configuration error: SECRET_KEY not set',
        )

    # 计算 HMAC-SHA256 签名
    expected_sign = hmac.new(
        secret_key.encode('utf-8'), sign_str.encode('utf-8'), hashlib.sha256
    ).hexdigest()

    # 使用恒定时间比较防止时序攻击
    if not hmac.compare_digest(expected_sign, signature):
        raise HTTPException(status_code=403, detail='Invalid signature')

    # 验证通过
    return True
