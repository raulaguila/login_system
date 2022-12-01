import os, json

from async_fastapi_jwt_auth.exceptions import MissingTokenError


with open(os.path.join(os.getcwd(), 'lang.json')) as file:
    languages: dict = json.load(file)


def translation(self, language: str):

    return languages[language]['exceptions'][self.__class__.__name__]


MissingTokenError.translation = translation


class TokenError(Exception):

    translation = translation


class PasswordsNotMatch(Exception):

    translation = translation


class UserCantDeleteYourself(Exception):

    translation = translation


class UserNotVerified(Exception):

    translation = translation


class UserNotFound(Exception):

    translation = translation


class UserAlredyExist(Exception):

    translation = translation


class UserNotActivated(Exception):

    translation = translation


class UserOrPasswordWrong(Exception):

    translation = translation


class LanguageUnsupported(Exception):

    translation = translation


class InvalidObjectId(Exception):

    translation = translation
