import os, asyncio, dotenv

from datetime import datetime
from pymongo import MongoClient
from passlib.context import CryptContext

from .exceptions import UserOrPasswordWrong, languages
from .database import connector
from .schemas.user import CreateUserSchema


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ADM_NAME = os.getenv('ADM_NAME') if os.getenv('ADM_NAME') else 'Administrator'
ADM_USER = os.getenv('ADM_USER') if os.getenv('ADM_USER') else 'admin@admin.com'
ADM_PASS = os.getenv('ADM_PASS') if os.getenv('ADM_PASS') else 'admin.2023'


async def start_request(lang: str, requester: dict) -> tuple:

    language = lang if lang in languages else os.getenv('SYS_LANGUAGE')

    if isinstance(requester, dict) and "role" in requester:
        is_admin = requester["role"] == "admin"
    else:
        is_admin = None

    return (is_admin, language)


async def load_env():

    dotenv.load_dotenv(override=True)


async def hash_password(password: str):

    return pwd_context.hash(password)


async def verify_password(password: str, hashed_password: str):

    if not pwd_context.verify(password, hashed_password):

        raise UserOrPasswordWrong()


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

    try:
        session = connector()
        client: MongoClient = await session.connect()
        await created_admin(client)
        await asyncio.sleep(0.5)
        await session.disconnect()
    except Exception as e:
        print(f"{e}")
