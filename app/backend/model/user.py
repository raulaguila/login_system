import os

from typing import Optional
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.results import UpdateResult, DeleteResult

from ..exceptions import *
from ..serializers.userSerializers import userResponseEntity


async def get_all(client: MongoClient, pipeline: list) -> Optional[list]:

    docs = list()

    async for doc in client[os.getenv('MONGO_BASE')]['users'].aggregate(pipeline, allowDiskUse=True):
        docs.append(userResponseEntity(doc))

    return docs


async def get_first(client: MongoClient, pipeline: list) -> Optional[dict]:

    async for doc in client[os.getenv('MONGO_BASE')]['users'].aggregate(pipeline, allowDiskUse=True):
        return doc

    raise UserNotFound('User not found.')


async def insert(client: MongoClient, document: dict) -> dict:
    filter = {'username':  document['username']}

    result: UpdateResult = await client[os.getenv('MONGO_BASE')]['users'].update_one(
        filter=filter,
        update={'$setOnInsert': document},
        upsert=True
    )

    if result.upserted_id is not None:

        pipeline = [{'$match': {'_id': ObjectId(str(result.upserted_id))}}]
        return await get_first(client, pipeline)

    raise UserAlredyExist('An account with this username already exists.')


async def update(client: MongoClient, filter: dict, update: dict) -> dict:

    result: UpdateResult = await client[os.getenv('MONGO_BASE')]['users'].update_one(
        filter=filter,
        update={"$set": update},
        upsert=False
    )

    if result.modified_count > 0:

        pipeline = [{'$match': filter}]
        return await get_first(client, pipeline)

    raise UserNotFound('User not found.')


async def delete(client: MongoClient, filter: dict) -> dict:

    deleted: DeleteResult = await client[os.getenv('MONGO_BASE')]['users'].delete_one(
        filter=filter
    )

    if deleted.deleted_count > 0:

        return True

    raise UserNotFound('User not found.')
