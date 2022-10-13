import os

from typing import Optional
from pymongo import MongoClient
from bson.objectid import ObjectId

from app.serializers.userSerializers import userResponseEntity

class userAlredyExist(Exception):
    pass



async def get_all(client: MongoClient, pipeline: list) -> Optional[list]:

    docs = list()

    async for doc in client[os.getenv('MONGO_BASE')]['users'].aggregate(pipeline, allowDiskUse=True):
        docs.append(userResponseEntity(doc))

    return docs


async def get_first(client: MongoClient, pipeline: list) -> Optional[dict]:

    async for doc in client[os.getenv('MONGO_BASE')]['users'].aggregate(pipeline, allowDiskUse=True):
        return doc

    return None


async def insert(client: MongoClient, document: dict) -> list:
    filter = { 'email': document['email'] }

    result = await client[os.getenv('MONGO_BASE')]['users'].update_one(
        filter=filter,
        update={'$setOnInsert': document},
        upsert=True
    )

    if result.upserted_id is not None:

        pipeline = [{'$match': {'_id': ObjectId(str(result.upserted_id))}}]
        return await get_first(client, pipeline)

    raise userAlredyExist('Email associated with another account.')
