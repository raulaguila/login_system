import os, asyncio

from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext

from .exceptions import *
from .database import *
from .schemas.user import CreateUserSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADM_NAME = os.getenv('ADM_NAME') if os.getenv('ADM_NAME') else 'Administrator'
ADM_USER = os.getenv('ADM_USER') if os.getenv('ADM_USER') else 'admin@admin.com'
ADM_PASS = os.getenv('ADM_PASS') if os.getenv('ADM_PASS') else 'admin.2023'


async def hash_password(password: str):

    return pwd_context.hash(password)


async def verify_password(password: str, hashed_password: str):

    if not pwd_context.verify(password, hashed_password):

        raise WrongUserOrPassword()


async def initialize_db():

    async def created_admin(client: MongoClient):

        adm_user = CreateUserSchema(
            name = ADM_NAME,
            username = ADM_USER,
            password = await hash_password(ADM_PASS),
            passwordConfirm = ADM_PASS,
            status = True,
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
    client: MongoClient = await session.connect()
    await created_admin(client)
    await asyncio.sleep(2)
    await session.disconnect()
