import urllib

from typing import Optional


class parameters(object):

    def __init__(self) -> None:
        self.host = None
        self.port = None
        self.username = None
        self.password = None
        self.database = None
        self.use_srv = False
        self.use_authenticator = False

    @property
    def host(self) -> Optional[str]:
        return self._host

    @host.setter
    def host(self, _host: str) -> None:
        assert _host is None or isinstance(_host, str), TypeError(f"\'host\' must be a string but received: {type(_host)}.")

        self._host = _host

    @property
    def port(self) -> Optional[int]:
        return self._port

    @port.setter
    def port(self, _port: int) -> None:
        assert _port is None or isinstance(_port, int), TypeError(f"\'port\' must be a integer but received: {type(_port)}.")
        assert _port is None or _port > 0, ValueError(f"\'port\' value cannot be a negative value, value: {_port}.")

        self._port = _port

    @property
    def username(self) -> Optional[str]:
        return self._username

    @username.setter
    def username(self, _username: str) -> None:
        assert _username is None or isinstance(_username, str), TypeError(f"\'username\' must be a string but received: {type(_username)}.")

        self._username = _username

    @property
    def password(self) -> Optional[str]:
        return self._password

    @password.setter
    def password(self, _password: str) -> None:
        assert _password is None or isinstance(_password, str), TypeError(f"\'password\' must be a string but received: {type(_password)}.")

        self._password = _password

    @property
    def database(self) -> Optional[str]:
        return self._database

    @database.setter
    def database(self, _database: str) -> None:
        assert _database is None or isinstance(_database, str), TypeError(f"\'database\' must be a string but received: {type(_database)}.")

        self._database = _database

    @property
    def use_srv(self) -> Optional[bool]:
        return self._use_srv

    @use_srv.setter
    def use_srv(self, _use_srv: bool) -> None:
        assert isinstance(_use_srv, bool), TypeError(f"\'use_srv\' must be a boolean but received: {type(_use_srv)}.")

        self._use_srv = _use_srv

    @property
    def use_authenticator(self) -> Optional[bool]:
        return self._use_authenticator

    @use_authenticator.setter
    def use_authenticator(self, _use_authenticator: bool) -> None:
        assert isinstance(_use_authenticator, bool), TypeError(f"\'use_authenticator\' must be a boolean but received: {type(_use_authenticator)}.")

        self._use_authenticator = _use_authenticator

    @property
    def uri(self) -> str:
        return self.__str__()

    def __str__(self) -> str:

        # Check if any value is None
        assert self.host is not None, ValueError(f"\'host\' not defined or is None, host value: {self.host}.")
        if not self.use_srv:
            assert self.port is not None, ValueError(f"\'port\' not defined or is None, port value: {self.port}.")
        if self.use_authenticator:
            assert self.username is not None, ValueError(f"\'username\' not defined or is None, username value: {self.username}.")
            assert self.password is not None, ValueError(f"\'password\' not defined or is None, password value: {self.password}.")
        assert self.database is not None, ValueError(f"\'database\' not defined or is None, database value: {self.database}.")

        # Create URI
        driver = f"mongodb{'+srv' if self.use_srv else ''}"
        authenticator = f'{self.username}:{urllib.parse.quote(self.password)}@' if self.use_authenticator else ''
        host = f"{self.host}{f':{self.port}' if not self.use_srv else ''}"

        return f'{driver}://{authenticator}{host}/{self.database}?authSource=admin&retryWrites=true&w=majority'
