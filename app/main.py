from dotenv import load_dotenv
load_dotenv()

import os
import aioredis
import app.routers as routers

from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware


app = FastAPI(
    title="API - API Rest",
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
    description="Documentations endpoints: \'/docs\' and \'/redocs\'.",
    docs_url="/docs",
    redoc_url="/redocs",
    swagger_ui_parameters = {"docExpansion":"none"},
)


app.include_router(routers.root.router, tags=['Root'])
app.include_router(routers.auth.router, tags=['Auth'], prefix='/auth')
app.include_router(routers.user.router, tags=['Users'], prefix='/users')


@app.on_event("startup")
async def startup_event():

    global redis

    if os.getenv('REDIS_PASS') is not None:
        redis =  aioredis.from_url(f"redis://{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}", encoding="utf8", decode_responses=True, password=os.environ['REDIS_PASS'])
    else:
        redis =  aioredis.from_url(f"redis://{os.environ['REDIS_HOST']}:{os.environ['REDIS_PORT']}", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fimis-cache")

    # print("API Started...")


@app.on_event("shutdown")
async def shutdown_event():

    global redis

    await redis.close()
    await redis.connection_pool.disconnect()

    # print("API Stoped...")
