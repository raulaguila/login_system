import motor.motor_asyncio as motor

from os import getenv, environ
from pymongo import MongoClient, errors

from .parameters import parameters


class connector:
    def __init__(self) -> None:

        self.client: MongoClient = None

    async def connect(self) -> MongoClient:

        try:

            params: parameters = parameters()
            params.host = environ['MONGO_HOST']
            params.port = int(environ['MONGO_PORT'])
            params.database =  'db_octopus'

            params.use_authenticator = bool(getenv('MONGO_PASS') and getenv('MONGO_USER'))

            if params.use_authenticator:

                params.username = environ['MONGO_USER']
                params.password = environ['MONGO_PASS']

            self.client = motor.AsyncIOMotorClient(params.uri)

        except Exception as e:

            print(f'Erro ao conectar com o mongo: {e}')

        return self.client

    async def disconnect(self):

        self.client.close()

    async def is_connected(self) -> bool:
        '''
        # Check if mongo is connected. Return True if connected else False.
        '''
        try:
            self.client.server_info()

            return True

        except errors.ServerSelectionTimeoutError as e:
            print(f'{e}')

        except errors.InvalidOperation as e:
            print(f'{e}')

        except AttributeError as e:
            print(f'{e}')

        except Exception as e:
            print(f'{e}')

        return False
