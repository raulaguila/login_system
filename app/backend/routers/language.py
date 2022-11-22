import os
import dotenv
import json


from fastapi import APIRouter, Response, status, HTTPException

from ..exceptions import *
from ..schemas import schema_lang
from ..serializers.languageSerializers import langResponseEntity


router = APIRouter(
    tags=['Language'],
    prefix='/lang',
)


@router.get('/', response_model=schema_lang.LanguageBaseSchema)
async def get_language():

    try:

        return langResponseEntity(os.getenv('SYS_LANGUAGE'))

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")


@router.put('/')
async def set_language(lang: schema_lang.LanguageBaseSchema):

    try:

        f = open(os.path.join(os.getcwd(), 'lang.json'))
        langs: dict = json.load(f)
        if not lang.language in langs.keys():
            raise LanguageUnsupported()

        dotenv.set_key(dotenv.find_dotenv(), 'SYS_LANGUAGE', str(lang.language))
        dotenv.load_dotenv(override=True)

        f.close()

        return Response(status_code=status.HTTP_200_OK)

    except LanguageUnsupported as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.translation())

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")
