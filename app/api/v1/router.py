from fastapi import APIRouter
from app.api.v1.endpoints import music

router = APIRouter()

router.include_router(
    music.router,  # 子路由
    prefix='/music',  # 所有接口路径前加上 /music
    tags=['音乐搜索'],  # 在 Swagger 文档中分组显示
)
