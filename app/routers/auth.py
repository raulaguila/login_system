import os

from typing import Optional
from datetime import timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, Cookie, responses

from .. import utils, oauth2
from ..exceptions import UserOrPasswordWrong, UserNotActivated, TokenError, UserNotFound, MissingTokenError, MissingTokenErro
from ..database import get_connection
from ..schemas import schema_user
from ..model import model_user
from ..serializers.userSerializers import userEntity

from pymongo import MongoClient


router = APIRouter(
    tags=['Auth'],
    prefix='/auth',
    dependencies=[Depends(utils.load_env)]
)

ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN"))
REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN"))


@router.post('/login')
async def login(payload: schema_user.LoginUserSchema, response: Response, Authorize: oauth2.AuthJWT = Depends(), client: MongoClient = Depends(get_connection), lang: Optional[str] = Cookie(None)):

    _, lang = await utils.start_request(lang, None)

    pipeline = [{'$match': {'username': payload.username.lower()}}]

    user = await model_user.get_first(client, pipeline)

    # Check if user exist and if password is valid
    if not user or not await utils.equals_passwords(payload.password, user['password']):

        raise UserOrPasswordWrong(lang=lang, status_code=status.HTTP_400_BAD_REQUEST)

    # Check if user is activated
    if not user['status']:

        raise UserNotActivated(lang=lang, status_code=status.HTTP_401_UNAUTHORIZED)

    user = userEntity(user)

    # Create access token
    access_token = await Authorize.create_access_token(subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    # Create refresh token
    refresh_token = await Authorize.create_refresh_token(subject=str(user["id"]), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

    # Store refresh and access tokens in cookie
    response.set_cookie(oauth2.COKIE_ACCESS_TOKEN, access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie(oauth2.COKIE_REFRESH_TOKEN, refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('lang', lang, None, None, '/', None, False, True, 'lax')

    # Send both access
    return {'status': 'success', 'access_token': access_token}


@router.get('/refresh')
async def refresh_token(response: Response, Authorize: oauth2.AuthJWT = Depends(), client: MongoClient = Depends(get_connection), lang: Optional[str] = Cookie(None)):

    try:
        _, lang = await utils.start_request(lang, None)

        await Authorize.jwt_refresh_token_required()

        user_id = await Authorize.get_jwt_subject()

        if not user_id:

            raise TokenError(lang=lang, status_code=status.HTTP_401_UNAUTHORIZED)

        pipeline = [{'$match': {'_id': ObjectId(str(user_id))}}]
        user = await model_user.get_first(client, pipeline)

        if not user:

            raise UserNotFound(lang=lang, status_code=status.HTTP_401_UNAUTHORIZED)

        user = userEntity(user)

        access_token = await Authorize.create_access_token(subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))
        refresh_token = await Authorize.create_refresh_token(subject=str(user["id"]), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

    except MissingTokenError:

        raise MissingTokenErro(lang=lang, status_code=status.HTTP_400_BAD_REQUEST)

    response.set_cookie(oauth2.COKIE_ACCESS_TOKEN, access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie(oauth2.COKIE_REFRESH_TOKEN, refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('lang', lang, None, None, '/', None, False, True, 'lax')

    return {'access_token': access_token}


@router.get('/logout', status_code=status.HTTP_200_OK)
async def logout(Authorize: oauth2.AuthJWT = Depends(), requester: dict = Depends(oauth2.require_user), lang: Optional[str] = Cookie(None)):

    _, lang = await utils.start_request(lang, requester)

    await Authorize.unset_jwt_cookies()

    response = responses.JSONResponse(status_code=status.HTTP_200_OK, content={'status': 'success'})
    response.delete_cookie(os.getenv('COKIE_ACCESS_TOKEN'))
    response.delete_cookie(os.getenv('COKIE_REFRESH_TOKEN'))
    response.set_cookie('lang', lang, None, None, '/', None, False, True, 'lax')

    return response
