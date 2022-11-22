import os

from datetime import timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException

from .. import utils, oauth2
from ..exceptions import *
from ..database import get_connection
from ..schemas import schema_user
from ..model import model_user
from ..serializers.userSerializers import userEntity

from pymongo import MongoClient

router = APIRouter(
    tags=['Auth'],
    prefix='/auth'
)

ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN"))
REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN"))


@router.post('/login')
async def login(payload: schema_user.LoginUserSchema, response: Response, Authorize: oauth2.AuthJWT = Depends(), client: MongoClient = Depends(get_connection)):
    # Check if the user exist
    try:
        pipeline = [{'$match': {'username': payload.username.lower()}}]

        user = await model_user.get_first(client, pipeline)

        if not user:
            raise UserOrPasswordWrong()

        # Check if the password is valid, except WrongPassword if is not valid
        await utils.verify_password(payload.password, user['password'])

        # Check if user is activated
        if not user['status']:
            raise UserNotActivated()

        user = userEntity(user)

        # Create access token
        access_token = await Authorize.create_access_token(subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

        # Create refresh token
        refresh_token = await Authorize.create_refresh_token(subject=str(user["id"]), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

        # Store refresh and access tokens in cookie
        response.set_cookie(oauth2.COKIE_ACCESS_TOKEN, access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
        response.set_cookie(oauth2.COKIE_REFRESH_TOKEN, refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

        # Send both access
        return {'status': 'success', 'access_token': access_token}

    except UserNotActivated as e:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.translation())

    except UserOrPasswordWrong as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.translation())


@router.get('/refresh')
async def refresh_token(response: Response, Authorize: oauth2.AuthJWT = Depends(), client: MongoClient = Depends(get_connection)):

    try:
        await Authorize.jwt_refresh_token_required()

        user_id = await Authorize.get_jwt_subject()

        if not user_id:

            raise TokenError()

        pipeline = [{'$match': {'_id': ObjectId(str(user_id))}}]
        user = await model_user.get_first(client, pipeline)
        if not user:
            UserNotFound()
        user = userEntity(user)

        access_token = await Authorize.create_access_token(subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
        refresh_token = await Authorize.create_refresh_token(subject=str(user["id"]), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

    except (UserNotFound, TokenError) as e:

        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=e.translation())

    except MissingTokenError as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.translation())

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}")

    response.set_cookie(oauth2.COKIE_ACCESS_TOKEN, access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie(oauth2.COKIE_REFRESH_TOKEN, refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')

    return {'access_token': access_token}


@router.get('/logout', status_code=status.HTTP_200_OK)
async def logout(Authorize: oauth2.AuthJWT = Depends(), requester: str = Depends(oauth2.require_user)):

    await Authorize.unset_jwt_cookies()

    return {'status': 'success'}
