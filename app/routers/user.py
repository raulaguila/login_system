import os

from typing import List, Optional
from fastapi import APIRouter, Depends, status, HTTPException, Response, Cookie
from bson.objectid import ObjectId
from pymongo import MongoClient
from datetime import datetime

from .. import utils, oauth2
from ..exceptions import PasswordsNotMatch, UserAlredyExist, InvalidObjectId, UserNotFound, UserCantDeleteYourself, UserNotAuthorized
from ..model import model_user
from ..schemas import schema_user
from ..database import get_connection
from ..serializers.userSerializers import userResponseEntity


router = APIRouter(
    tags=['Users'],
    prefix='/user',
    dependencies=[Depends(utils.load_env)]
)


@router.get('/me', response_model=schema_user.UserResponseSchema)
async def get_me(requester: dict = Depends(oauth2.require_user)):

    return userResponseEntity(requester)


@router.get('/all', response_model=List[schema_user.UserResponseSchema], status_code=status.HTTP_200_OK)
async def get_all(requester: dict = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection)):

    return await model_user.get_all(client, [])


@router.post('/new', status_code=status.HTTP_201_CREATED, response_model=schema_user.UserResponseSchema)
async def create_user(payload: schema_user.CreateUserSchema, requester: dict = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection), lang: Optional[str] = Cookie(None)):

    try:
        is_admin, lang = await utils.start_request(lang, requester)

        if not is_admin:

            raise UserNotAuthorized()

        # Compare password and passwordConfirm
        if payload.password != payload.passwordConfirm:

            raise PasswordsNotMatch()

        #  Hash the password
        payload.password = await utils.hash_password(payload.password)
        del payload.passwordConfirm
        # payload.role = 'admin'
        payload.username = payload.username.lower()
        payload = payload.dict()
        payload['created_at'] = datetime.now()
        payload['updated_at'] = payload['created_at']

        new_user = await model_user.insert(client, payload)
        if not new_user:
            raise UserAlredyExist()

        return userResponseEntity(new_user)


    except PasswordsNotMatch as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.translation(lang))

    except UserAlredyExist as e:

        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=e.translation(lang))

    except UserNotAuthorized as e:

        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.translation(lang))

    except Exception as e:

        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'{e}')


@router.get('/{id}', response_model=schema_user.UserResponseSchema, status_code=status.HTTP_200_OK)
async def get_user(id: str, requester: dict = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection), lang: Optional[str] = Cookie(None)):

    try:
        is_admin, lang = await utils.start_request(lang, requester)

        if not ObjectId.is_valid(id):
            raise InvalidObjectId()

        pipeline = [{'$match': {'_id': ObjectId(id)}}]
        user = await model_user.get_first(client, pipeline)
        if not user:
            raise UserNotFound()

        return userResponseEntity(user)

    except InvalidObjectId as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.translation(lang))

    except UserNotFound as e:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.translation(lang))


@router.put('/{id}', response_model=schema_user.UserResponseSchema, status_code=status.HTTP_200_OK)
async def update_user(id: str, payload: schema_user.UpdateUserSchema, requester: dict = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection), lang: Optional[str] = Cookie(None)):

    try:
        is_admin, lang = await utils.start_request(lang, requester)

        if not is_admin:
            raise UserNotAuthorized()

        if not ObjectId.is_valid(id):
            raise InvalidObjectId()

        if payload.password and payload.password != payload.passwordConfirm:
            raise PasswordsNotMatch()

        del payload.passwordConfirm
        if payload.password:
            payload.password = await utils.hash_password(payload.password)
        else:
            del payload.password

        if not payload.role:
            del payload.role

        if not payload.photo:
            del payload.photo

        if not payload.email:
            del payload.email

        pipeline = [{'$match': {'username': str(payload.username).lower()}}]
        user = await model_user.get_first(client, pipeline)
        if user:
            user = userResponseEntity(user)
            if user['id'] != id:
                raise UserAlredyExist()

        payload.username = payload.username.lower()
        payload = payload.dict()
        payload['updated_at'] = datetime.now()

        filter = {'_id': ObjectId(id)}
        user = await model_user.update(client, filter, payload)

        if not user:
            raise UserNotFound()

        return userResponseEntity(user)

    except (InvalidObjectId, UserAlredyExist, PasswordsNotMatch) as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.translation(lang))

    except UserNotAuthorized as e:

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.translation(lang))

    except UserNotFound as e:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.translation(lang))


@router.delete('/{id}', status_code=status.HTTP_200_OK)
async def delete_user(id: str, requester: dict = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection), lang: Optional[str] = Cookie(None)):

    try:
        is_admin, lang = await utils.start_request(lang, requester)

        if not is_admin:
            raise UserNotAuthorized()

        if not ObjectId.is_valid(id):
            raise InvalidObjectId()

        if str(requester['_id']) == id:
            raise UserCantDeleteYourself()

        filter = {'_id': ObjectId(id)}

        if not await model_user.delete(client, filter):
            raise UserNotFound()

        return Response(status_code=status.HTTP_200_OK)

    except InvalidObjectId as e:

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.translation(lang))

    except (UserCantDeleteYourself, UserNotAuthorized) as e:

            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=e.translation(lang))

    except UserNotFound as e:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.translation(lang))
