import os, asyncio

from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext

from .database import *
from .schemas.user import CreateUserSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ADM_NAME = os.getenv('ADM_NAME') if os.getenv('ADM_NAME') else 'Administrator'
ADM_USER = os.getenv('ADM_USER') if os.getenv('ADM_USER') else 'admin@admin.com'
ADM_PASS = os.getenv('ADM_PASS') if os.getenv('ADM_PASS') else 'admin.2023'


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str):
    return pwd_context.verify(password, hashed_password)


async def initialize_db():

    async def created_admin(client: MongoClient):

        adm_user = CreateUserSchema(
            name = ADM_NAME,
            username = ADM_USER,
            password = hash_password(ADM_PASS),
            passwordConfirm= ADM_PASS,
            role = 'admin'
        )

        del adm_user.passwordConfirm
        adm_user = adm_user.dict()
        adm_user['created_at'] = datetime.now()
        adm_user['updated_at'] = adm_user['created_at']
        filter = {'username':  ADM_USER.lower()}

        await client[os.getenv('MONGO_BASE')]['users'].update_one(
            filter=filter,
            update={'$setOnInsert': adm_user},
            upsert=True
        )

    session = connector()
    await created_admin(await session.connect())
    await asyncio.sleep(2)
    await session.disconnect()
