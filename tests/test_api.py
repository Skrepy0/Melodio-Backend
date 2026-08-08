import hashlib
import hmac
import json
import sys
import time

import httpx
import pytest
from httpx import AsyncClient, ASGITransport

from app.core.config import settings
from main import app

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
        'music_client': ['KuwoMusicClient', 'MiguMusicClient'],
        'limit': 5,
        'timeout': 1,
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
    print(response.json())


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


@pytest.mark.asyncio
async def test_parse_song_list_success():
    """测试: 正常解析歌单, 返回200"""
    params = {
        'url': 'https://h5app.kuwo.cn/m/bodian/collection.html?uid=45780003&playlistId=86749638&source=5&owerId=',
        'music_client': ['BodianMusicClient'],
        'limit': 2,
    }
    headers = make_signed_headers(
        path='/api/v1/music/parse_song_list', params=params
    )
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        response = await client.get(
            '/api/v1/music/parse_song_list', params=params, headers=headers
        )
    data = response.json()
    assert response.status_code == 200, (
        f'Unexpected status {response.status_code}: {data}'
    )
    assert 'total' in data
    assert 'items' in data


@pytest.mark.asyncio
async def test_parse_song_list_client_count_mismatch():
    """测试: 音乐来源数量不匹配, 返回422"""
    params = {
        'url': 'https://h5app.kuwo.cn/m/bodian/collection.html?uid=45780003&playlistId=86749638&source=5&owerId=',
        'music_client': ['BodianMusicClient', 'BilibiliMusicClient'],
        'limit': 2,
    }
    headers = make_signed_headers(
        path='/api/v1/music/parse_song_list', params=params
    )
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        response = await client.get(
            '/api/v1/music/parse_song_list', params=params, headers=headers
        )
    data = response.json()
    assert response.status_code == 422, (
        f'Unexpected status {response.status_code}: {data}'
    )
    assert 'code' in data
    assert 'msg' in data
    assert 'detail' in data


@pytest.mark.asyncio
async def test_search_stream_success():
    """测试 SSE 搜索成功：应返回流式数据并最终收到 done"""
    params = {
        'keyword': '林俊杰',
        'music_client': ['KuwoMusicClient', 'MiguMusicClient'],
        'limit': 3,
        'timeout': 30,
    }
    headers = make_signed_headers(
        path='/api/v1/music/search_stream', params=params
    )
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url='http://test'
    ) as client:
        async with client.stream(
                'GET',
                '/api/v1/music/search_stream',
                params=params,
                headers=headers,
        ) as response:
            assert response.status_code == 200
            assert response.headers['content-type'].startswith(
                'text/event-stream'
            )

            received_sources = set()
            done_received = False

            async for line in response.aiter_lines():
                if not line.startswith('data: '):
                    continue
                data_str = line[6:].strip()
                if not data_str:
                    continue
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError:
                    continue

                if data.get('status') == 'done':
                    done_received = True
                    break

                assert data.get('status') == 'partial'
                assert 'source' in data
                assert 'items' in data
                assert isinstance(data['items'], list)
                received_sources.add(data['source'])

            assert done_received, "未收到结束信号 'done'"
            assert len(received_sources) >= 1, '至少应有一个音乐源返回结果'
