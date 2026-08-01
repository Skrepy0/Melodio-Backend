from fastapi import APIRouter, Depends, Query, HTTPException
from app.schemas.music import SongResponse
from app.core.dependencies import verify_signature

router = APIRouter()


@router.get(
    '/search',
    response_model=SongResponse,
    summary='搜索歌曲',
    description='根据关键词搜索歌曲',
)
async def search_songs(
    # Query 参数
    keyword: str = Query(
        ..., min_length=1, max_length=100, description='搜索关键词'
    ),
    limit: int = Query(10, ge=1, le=50, description='返回条数，最大 50'),
    # 签名校验
    _: bool = Depends(verify_signature),
):
    # TODO
    return SongResponse(total=0, items=[])
