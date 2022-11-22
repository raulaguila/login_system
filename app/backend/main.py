from dotenv import load_dotenv
load_dotenv()

import os
import time

from redis import asyncio as aioredis
from fastapi import FastAPI, Request, status, Response
from fastapi.responses import JSONResponse
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from .routers import *
from .utils import initialize_db


doc_endpoint = os.getenv('DOC_ENDPOINT')
redoc_endpoint = os.getenv('REDOC_ENDPOINT')
json_endpoint = os.getenv('JSON_ENDPOINT')


app = FastAPI(
    title="API - Authentication API",
    version=os.getenv('SYS_VERSION') if os.getenv('SYS_VERSION') else '1.0.0',
    middleware=[Middleware(
        CORSMiddleware,
        allow_credentials=True,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        max_age=1
    )],
    debug=False,
    description=f"Documentations endpoints: {doc_endpoint} and {redoc_endpoint}.",
    docs_url=doc_endpoint,
    redoc_url=redoc_endpoint,
    openapi_url=json_endpoint,
    swagger_ui_parameters = {"docExpansion":"none"}
)


app.include_router(root.router)
app.include_router(language.router)
app.include_router(auth.router)
app.include_router(user.router)


@app.exception_handler(Exception)
async def exception_callback(request: Request, exc: Exception):

    request_info: dict = {
        'url': f'{request.url}',
        'path_params': request.path_params,
        'query_params': f'{request.query_params}',
        # 'body': f'{(await request.json())}',
        # 'cookies': request.cookies
    }

    return JSONResponse(
        status_code=status.HTTP_418_IM_A_TEAPOT,
        content={
            'message': f'Something wrong [{exc.__class__.__name__}]: {exc}',
            'request': request_info
        },
    )


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):

    start_time = time.time()
    response: Response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Version"] = f"{os.getenv('SYS_VERSION')}"

    return response


@app.on_event("startup")
async def startup_event():

    global redis

    if os.getenv('REDIS_PASS') is not None:
        redis =  aioredis.from_url(f"redis://{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}", encoding="utf8", decode_responses=True, password=os.environ['REDIS_PASS'])
    else:
        redis =  aioredis.from_url(f"redis://{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}", encoding="utf8", decode_responses=True)

    FastAPICache.init(RedisBackend(redis), prefix="fimis-cache")

    try:
        await initialize_db()
    except Exception as e:
        print(f"{e}")


@app.on_event("shutdown")
async def shutdown_event():

    global redis

    await redis.close()
    await redis.connection_pool.disconnect()
