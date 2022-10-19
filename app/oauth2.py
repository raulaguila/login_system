import os
import base64

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi_jwt_auth import AuthJWT
from pydantic import BaseModel
from bson.objectid import ObjectId

from app.database import connector
from app.model import model_user
from .serializers.userSerializers import userEntity


class Settings(BaseModel):

    authjwt_algorithm: str = os.getenv("JWT_ALGORITHM")
    authjwt_decode_algorithms: List[str] = [os.getenv("JWT_ALGORITHM")]
    authjwt_token_location: set = {'cookies', 'headers'}
    authjwt_access_cookie_key: str = 'access_token'
    authjwt_refresh_cookie_key: str = 'refresh_token'
    authjwt_cookie_csrf_protect: bool = False
    authjwt_public_key: str = base64.b64decode(os.getenv("JWT_PUBLIC_KEY")).decode('utf-8')
    authjwt_private_key: str = base64.b64decode(os.getenv("JWT_PRIVATE_KEY")).decode('utf-8')


@AuthJWT.load_config
def get_config():
    return Settings()


class NotVerified(Exception):
    pass


class UserNotFound(Exception):
    pass


async def require_user(Authorize: AuthJWT = Depends()):

    try:
        conn = connector()
        client = await conn.connect()

        Authorize.jwt_required()
        user_id = Authorize.get_jwt_subject()
        pipeline = [{'$match': {'_id': ObjectId(str(user_id))}}]
        user = await model_user.get_first(client, pipeline)

        if not user:
            raise UserNotFound()

        if not user["verified"]:
            raise NotVerified()

        user = userEntity(user)

    except Exception as e:
        error = e.__class__.__name__

        match error:

            case 'MissingTokenError':

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='You are not logged in.')

            case 'UserNotFound':

                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The user does not exist.')

            case 'NotVerified':

                raise HTTPException(tatus_code=status.HTTP_401_UNAUTHORIZED, detail='Please verify your account.')

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Token is invalid or has expired.')

    try:
        await conn.disconnect()
    except Exception:
        pass

    return user_id
