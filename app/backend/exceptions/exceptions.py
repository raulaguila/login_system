class NotVerified(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserNotFound(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserAlredyExist(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
