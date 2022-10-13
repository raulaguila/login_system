import os

from datetime import datetime, timedelta
from bson.objectid import ObjectId
from fastapi import APIRouter, Response, status, Depends, HTTPException

from app.database import get_connection
from app.serializers import userEntity, userResponseEntity
from .. import utils, oauth2
from app.schemas import schema_user
from pymongo import MongoClient
from app.model import model_user

router = APIRouter()

ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN"))
REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN"))


@router.post('/register', status_code=status.HTTP_201_CREATED, response_model=schema_user.UserResponseSchema)
# async def create_user(payload: user.CreateUserSchema, user_id: str = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection)):
async def create_user(payload: schema_user.CreateUserSchema, client: MongoClient = Depends(get_connection)):

    # Compare password and passwordConfirm
    if payload.password != payload.passwordConfirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Passwords do not match.')

    #  Hash the password
    payload.password = utils.hash_password(payload.password)
    del payload.passwordConfirm
    payload.role = 'admin'
    payload.verified = True
    payload.email = payload.email.lower()
    payload.created_at = datetime.utcnow()
    payload.updated_at = payload.created_at

    try:

        new_user = userResponseEntity(await model_user.insert(client, payload.dict()))
        return new_user

    except Exception as e:
        error = e.__class__.__name__

        if error == 'userAlredyExist':
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'{e}')

        print(f'{e}')
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'{e}')


@router.post('/login')
async def login(payload: schema_user.LoginUserSchema, response: Response, Authorize: oauth2.AuthJWT = Depends(), client: MongoClient = Depends(get_connection)):
    # Check if the user exist
    pipeline = [{'$match': {'email': payload.email.lower()}}]
    user = await model_user.get_first(client, pipeline)

    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Email or Password')

    # Check if user verified his email
    if not user['verified']:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Please verify your email address')

    # Check if the password is valid
    if not utils.verify_password(payload.password, user['password']):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Incorrect Email or Password')

    user = userEntity(user)

    # Create access token
    access_token = Authorize.create_access_token(subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(subject=str(user["id"]), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN))

    # Store refresh and access tokens in cookie
    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('refresh_token', refresh_token, REFRESH_TOKEN_EXPIRES_IN * 60, REFRESH_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    # Send both access
    return {'status': 'success', 'access_token': access_token}


@router.get('/refresh')
async def refresh_token(response: Response, Authorize: oauth2.AuthJWT = Depends(), client: MongoClient = Depends(get_connection)):
    try:
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()

        if not user_id:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not refresh access token')

        pipeline = [{'$match': {'_id': ObjectId(str(user_id))}}]
        user = userEntity(await model_user.get_first(client, pipeline))

        if not user:

            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='The user belonging to this token no logger exist')

        access_token = Authorize.create_access_token(subject=str(user["id"]), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN))

    except Exception as e:

        error = e.__class__.__name__

        if error == 'MissingTokenError':
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Please provide refresh token')

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    response.set_cookie('access_token', access_token, ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, True, 'lax')
    response.set_cookie('logged_in', 'True', ACCESS_TOKEN_EXPIRES_IN * 60, ACCESS_TOKEN_EXPIRES_IN * 60, '/', None, False, False, 'lax')

    return {'access_token': access_token}


@router.get('/logout', status_code=status.HTTP_200_OK)
def logout(response: Response, Authorize: oauth2.AuthJWT = Depends(), user_id: str = Depends(oauth2.require_user)):

    Authorize.unset_jwt_cookies()
    response.set_cookie('logged_in', '', -1)

    return {'status': 'success'}
