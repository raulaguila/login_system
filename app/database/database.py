from typing import AsyncGenerator
from fastapi import HTTPException, status
from pymongo.errors import OperationFailure, InvalidOperation

from .mongo.connector import connector


async def get_connection() -> AsyncGenerator:

    try:

        session = connector()
        client = await session.connect()

    except OperationFailure as e:

        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"{e}")

    try:
        try:
            yield client
        finally:
            await session.disconnect()
    except InvalidOperation:

        pass
