from typing import List
from pydantic import BaseModel


class LanguageBaseSchema(BaseModel):
    code: str
    language: str
