from typing import List
from pydantic import BaseModel


class LanguageBaseSchema(BaseModel):
    language: str


class SupportedLanguagesSchema(BaseModel):
    languages: List[str]
