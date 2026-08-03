import sys
from urllib.parse import urlencode

import httpx
import pytest
import hmac
import hashlib
import time
from httpx import AsyncClient, ASGITransport
from main import app
from app.core.config import settings

print('Python:', sys.executable)
print('httpx:', httpx.__version__)


def make_signed_headers(
    method='GET', path='/api/v1/music/search', params=None
):
    if params is None:
        params = {'keyword': '林俊杰', 'limit': 5}

    items = []
    for k, v in params.items():
        if isinstance(v, list):
            for item in v:
                items.append((k, item))
        else:
            items.append((k, v))

    sorted_items = sorted(items)

    query_str = '&'.join([f'{k}={v}' for k, v in sorted_items])

    timestamp = str(int(time.time()))
    nonce = 'pytest_nonce'
    sign_str = f'{method}&{path}&{query_str}&{timestamp}&{nonce}'
    print('🔵 TEST sign_str:', repr(sign_str))
    signature = hmac.new(
        settings.SECRET_KEY.encode('utf-8'),
        sign_str.encode('utf-8'),
        hashlib.sha256,
    ).hexdigest()
    return {
        'X-Timestamp': timestamp,
        'X-Nonce': nonce,
        'X-Signature': signature,
    }


@pytest.mark.asyncio
async def test_search_success():
    """测试: 正常搜索，应返回 200"""
    params = {
        'keyword': '有兽焉',
        'music_client': ['BilibiliMusicClient', 'KuwoMusicClient'],
        'limit': 5,
    }
    headers = make_signed_headers(params=params)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        response = await client.get(
            '/api/v1/music/search', params=params, headers=headers
        )
    assert response.status_code == 200, (
        f'Unexpected status {response.status_code}: {response.text}'
    )


@pytest.mark.asyncio
async def test_search_missing_signature():
    """测试: 缺少请求签名, 返回 403"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        response = await client.get(
            '/api/v1/music/search', params={'keyword': 'test'}
        )
    assert response.status_code == 403
    assert 'Missing signature' in response.text


@pytest.mark.asyncio
async def test_search_invalid_signature():
    """测试: 无效请求签名，返回 403"""
    params = {'keyword': 'test'}
    headers = {
        'X-Timestamp': str(int(time.time())),
        'X-Nonce': 'abc',
        'X-Signature': 'this_is_wrong_signature',
    }
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        response = await client.get(
            '/api/v1/music/search', params=params, headers=headers
        )
    assert response.status_code == 403
    assert 'Invalid signature' in response.text


@pytest.mark.asyncio
async def test_search_invalid_music_client():
    """测试: 无效音乐来源, 返回422"""
    params = {
        'keyword': '林俊杰',
        'music_client': ['ZzgMusicClient'],
        'limit': 5,
    }
    headers = make_signed_headers(params=params)
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        response = await client.get(
            '/api/v1/music/search', params=params, headers=headers
        )
    assert response.status_code == 422
    data = response.json()
    assert 'code' in data
    assert 'msg' in data
    assert 'detail' in data
