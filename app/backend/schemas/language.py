from pydantic import BaseModel


class LanguageBaseSchema(BaseModel):
    language: str
