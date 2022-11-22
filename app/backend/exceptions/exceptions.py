import os, json, dotenv

from async_fastapi_jwt_auth.exceptions import MissingTokenError


class translate:

    def translation(self, class_name: str) -> str:

        f = open(os.path.join(os.getcwd(), 'lang.json'))
        lang = json.load(f)
        dotenv.load_dotenv(override=True)
        translation_ : str = lang[os.getenv('SYS_LANGUAGE')]['exceptions'][f'{class_name}']
        f.close()

        return translation_


def translation(self):

    return translate().translation(self.__class__.__name__)


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
