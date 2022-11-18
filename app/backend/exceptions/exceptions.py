class NotVerified(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserNotFound(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserAlredyExist(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class UserNotActivated(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class WrongUserOrPassword(Exception):

    def __init__(self, *args: object) -> None:
        super().__init__(*args)
