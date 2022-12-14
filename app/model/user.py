import os
import asyncio

from typing import Optional, List
from pymongo import ASCENDING
from pymongo import MongoClient
from bson.objectid import ObjectId
from pymongo.results import UpdateResult, DeleteResult

from ..serializers.userSerializers import userResponseListEntity


async def create_indexes(client: MongoClient) -> bool:

    try:

        keys: list = ['username', 'status', 'role']

        for key in keys:

            await client[os.getenv('MONGO_BASE')]['users'].create_index([(key, ASCENDING)], background=False)

        await asyncio.sleep(1e-3)

        return True

    except Exception as e:

        print(f"Error to create index: {e}")

    return False


async def get_all(client: MongoClient, pipeline: List[dict]) -> Optional[list]:

    docs = list()

    async for doc in client[os.getenv('MONGO_BASE')]['users'].aggregate(pipeline, allowDiskUse=True):
        docs.append(doc)

    return userResponseListEntity(docs)


async def get_first(client: MongoClient, pipeline: List[dict]) -> Optional[dict]:

    async for doc in client[os.getenv('MONGO_BASE')]['users'].aggregate(pipeline, allowDiskUse=True):
        return doc

    return False


async def insert(client: MongoClient, document: dict) -> dict:
    filter = {'username':  document['username']}

    result: UpdateResult = await client[os.getenv('MONGO_BASE')]['users'].update_one(
        filter=filter,
        update={'$setOnInsert': document},
        upsert=True
    )

    if result.upserted_id is not None:

        if await create_indexes(client=client):

            pipeline = [{'$match': {'_id': ObjectId(str(result.upserted_id))}}]
            return await get_first(client, pipeline)

    return False


async def update(client: MongoClient, filter: dict, update: dict) -> dict:

    result: UpdateResult = await client[os.getenv('MONGO_BASE')]['users'].update_one(
        filter=filter,
        update={"$set": update},
        upsert=False
    )

    if result.modified_count > 0:

        if await create_indexes(client=client):

            pipeline = [{'$match': filter}]
            return await get_first(client, pipeline)

    return False


async def delete(client: MongoClient, filter: dict) -> dict:

    deleted: DeleteResult = await client[os.getenv('MONGO_BASE')]['users'].delete_one(
        filter=filter
    )

    return deleted.deleted_count > 0
