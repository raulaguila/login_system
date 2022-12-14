import os, json

from async_fastapi_jwt_auth.exceptions import MissingTokenError


with open(os.path.join(os.getcwd(), 'lang.json')) as file:
    languages: dict = json.load(file)


class APIBaseException(Exception):

    def __init__(self, lang: str, status_code: int) -> None:

        self.language = lang
        self.status_code = status_code

    def translation(self):

        return languages[self.language]['exceptions'][self.__class__.__name__]


class MissingTokenErro(APIBaseException):

    pass


class TokenError(APIBaseException):

    pass


class TokenInvalid(APIBaseException):

    pass


class PasswordsNotMatch(APIBaseException):

    pass


class UserNotAuthorized(APIBaseException):

    pass


class UserCantDeleteYourself(APIBaseException):

    pass


class UserNotVerified(APIBaseException):

    pass


class UserNotFound(APIBaseException):

    pass


class UserAlredyExist(APIBaseException):

    pass


class UserNotActivated(APIBaseException):

    pass


class UserOrPasswordWrong(APIBaseException):

    pass


class LanguageUnsupported(APIBaseException):

    pass


class InvalidObjectId(APIBaseException):

    pass
