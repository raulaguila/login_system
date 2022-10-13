from typing import List
from fastapi import APIRouter, Depends, status
from bson.objectid import ObjectId
from app.serializers.userSerializers import userResponseEntity
from pymongo import MongoClient

from .. import oauth2

from app.schemas import schema_user
from app.database import get_connection
from app.model import model_user

router = APIRouter()


@router.get('/me', response_model=schema_user.UserResponseSchema)
async def get_me(user_id: str = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection)):

    pipeline = [{'$match': {'_id': ObjectId(str(user_id))}}]
    user = userResponseEntity(await model_user.get_first(client, pipeline))

    return user


@router.get('/all', response_model=List[schema_user.UserResponseSchema], status_code=status.HTTP_200_OK)
async def get_all(user_id: str = Depends(oauth2.require_user), client: MongoClient = Depends(get_connection)):

    return await model_user.get_all(client, [])
