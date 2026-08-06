import hashlib
import hmac
import time
from urllib.parse import parse_qsl

from slowapi import Limiter
from fastapi import Request, HTTPException
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(key_func=get_remote_address, default_limits=['100/day'])


def verify_signature(request: Request):
    if request.method == 'OPTIONS':
        return True
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

    # 从原始查询字符串解析参数（保留重复键）
    raw_query = request.scope.get('query_string', b'').decode()
    # parse_qsl 返回列表，保留重复键
    query_items = parse_qsl(raw_query, keep_blank_values=True)

    # 过滤掉 timestamp 和 nonce
    filtered_items = [
        (k, v) for k, v in query_items if k not in ('timestamp', 'nonce')
    ]

    # 按字典序排序
    sorted_items = sorted(filtered_items)
    query_str = '&'.join([f'{k}={v}' for k, v in sorted_items])

    # 构建 sign_str
    sign_str = f'{method}&{path}&{query_str}&{timestamp}&{nonce}'
    print('🔴 SERVER sign_str:', repr(sign_str))
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
