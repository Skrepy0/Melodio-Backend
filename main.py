from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.api.v1.router import router as v1_router
import logging

from app.utils.exceptions import InvalidMusicClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info('应用启动中...')
    yield
    logger.info('应用关闭中...')


app = FastAPI(
    title='melodio api',
    description='Melodio的后端(基于 musicdl)',
    version='1.0.0',
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(v1_router, prefix='/api/v1')


@app.exception_handler(InvalidMusicClientError)
async def invalid_music_client_handler(
    request: Request, exc: InvalidMusicClientError
):
    return JSONResponse(
        status_code=422,
        content={
            'code': exc.code,
            'msg': f'Invalid music client: {exc.client_name}',
            'detail': str(exc),
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    捕获所有未处理的异常，返回统一格式的 JSON 错误响应
    """
    logger.error(f'全局异常: {exc}', exc_info=True)
    return JSONResponse(
        status_code=500,
        content={'code': 500, 'msg': f'服务器内部错误: {str(exc)}'},
    )


@app.get('/health', tags=['系统'])
async def health_check():
    return {'status': 'ok', 'version': '1.0.0'}


@app.get('/', tags=['系统'])
async def root():
    return {
        'message': '音乐搜索 API 服务已启动',
        'health': '/health',
        'docs': '/docs',
    }


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True,
    )
