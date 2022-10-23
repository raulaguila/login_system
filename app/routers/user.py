from typing import List
from fastapi import APIRouter, Depends, status, HTTPException
from bson.objectid import ObjectId
from pymongo import MongoClient

from .. import oauth2

from app.model import model_user
from app.schemas import schema_user
from app.database import get_connection
from app.serializers.userSerializers import userResponseEntity


router = APIRouter(
    tags=['Users'],
    prefix='/users',
    dependencies=[Depends(oauth2.require_user)]
)


@router.get('/me', response_model=schema_user.UserResponseSchema)
async def get_me(logged: dict = Depends(oauth2.require_user)):

    return userResponseEntity(logged)


@router.get('/all', response_model=List[schema_user.UserResponseSchema], status_code=status.HTTP_200_OK)
async def get_all(client: MongoClient = Depends(get_connection)):

    return await model_user.get_all(client, [])


@router.get('/{id}', response_model=schema_user.UserResponseSchema, status_code=status.HTTP_200_OK)
async def get_user(id: str, client: MongoClient = Depends(get_connection)):

    if not ObjectId.is_valid(id):

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Invalid ID.')

    pipeline = [{'$match': {'_id': ObjectId(id)}}]
    user = await model_user.get_first(client, pipeline)

    if not user:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found.')

    return userResponseEntity(user)
