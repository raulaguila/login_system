import os

from fastapi import APIRouter, Response, status
from fastapi.responses import RedirectResponse
from fastapi_cache.decorator import cache

from ..exceptions import *


router = APIRouter(
    tags=['Root']
)


@router.get('/')
async def documentation():

    doc_endpoint = os.getenv('DOC_ENDPOINT')
    return RedirectResponse(url=doc_endpoint, status_code=status.HTTP_308_PERMANENT_REDIRECT)


@router.get('/ping')
@cache(expire=60)
async def ping():

    return Response(status_code=status.HTTP_200_OK)
