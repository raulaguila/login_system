from typing import Optional, List
from fastapi import APIRouter, Response, status, Depends, Cookie, responses

from ..exceptions import LanguageUnsupported
from ..schemas import schema_lang
from ..serializers.languageSerializers import langResponseEntity
from ..utils import load_env, start_request, languages


router = APIRouter(
    tags=['Language'],
    prefix='/lang',
    dependencies=[Depends(load_env)]
)


@router.get('/', response_model=schema_lang.LanguageBaseSchema)
async def get_language(lang: Optional[str] = Cookie(None)):

    _, lang = await start_request(lang, None)

    response = responses.JSONResponse(status_code=status.HTTP_200_OK, content=langResponseEntity(lang, languages[lang]['language']))
    response.set_cookie('lang', lang, None, None, '/', None, False, True, 'lax')

    return response


@router.get('/all', response_model=List[schema_lang.LanguageBaseSchema])
async def get_supported_languages():

    return [langResponseEntity(key, value['language']) for key, value in languages.items()]


@router.put('/', response_model=None)
async def set_language(language: str, lang: Optional[str] = Cookie(None)):

    _, lang = await start_request(lang, None)

    if not language in languages:

        raise LanguageUnsupported(lang=lang, status_code=status.HTTP_400_BAD_REQUEST)

    response = Response(status_code=status.HTTP_200_OK)
    response.set_cookie('lang', language, None, None, '/', None, False, True, 'lax')

    return response
