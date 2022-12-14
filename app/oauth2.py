import os
import base64

from typing import List, Optional
from fastapi import Depends, status, Cookie
from async_fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from bson.objectid import ObjectId

from .exceptions import MissingTokenError, MissingTokenErro, TokenInvalid, UserNotFound, UserNotActivated
from .database import connector
from .model import model_user
from .utils import start_request


COKIE_ACCESS_TOKEN = os.getenv('COKIE_ACCESS_TOKEN') if os.getenv('COKIE_ACCESS_TOKEN') else 'access_token'
COKIE_REFRESH_TOKEN = os.getenv('COKIE_REFRESH_TOKEN') if os.getenv('COKIE_REFRESH_TOKEN') else  'refresh_token'
ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN"))
REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN"))


class Settings(BaseModel):

    authjwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    authjwt_decode_algorithms: List[str] = [os.getenv("JWT_ALGORITHM")]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = COKIE_ACCESS_TOKEN
    authjwt_refresh_cookie_key: str = COKIE_REFRESH_TOKEN
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = base64.b64decode(os.getenv("JWT_PUBLIC_KEY")).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(os.getenv("JWT_PRIVATE_KEY")).decode('utf-8')


@AuthJWT.load_config
def get_config():

    return Settings()


async def require_user(Authorize: AuthJWT = Depends(), lang: Optional[str] = Cookie(None)):

    _, lang = await start_request(lang, None)

    try:

        await Authorize.jwt_required()
        user_id = await Authorize.get_jwt_subject()

    except MissingTokenError:
        raise MissingTokenErro(lang=lang, status_code=status.HTTP_401_UNAUTHORIZED)

    except Exception:
        raise TokenInvalid(lang=lang, status_code=status.HTTP_401_UNAUTHORIZED)

    conn = connector()
    client = await conn.connect()
    user = await model_user.get_first(client, [{'$match': {'_id': ObjectId(str(user_id))}}])
    await conn.disconnect()

    if not user:
        raise UserNotFound(lang=lang, status_code=status.HTTP_401_UNAUTHORIZED)

    if not user['status']:
        raise UserNotActivated(lang=lang, status_code=status.HTTP_401_UNAUTHORIZED)

    return user
