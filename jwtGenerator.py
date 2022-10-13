import os
import jwt
from dotenv import load_dotenv
load_dotenv()

encoded_jwt = jwt.encode({"some": "payload"}, "secret", algorithm=os.getenv('JWT_ALGORITHM'))
