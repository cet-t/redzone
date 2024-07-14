import utility


class Core:
    def __init__(self, token_name: str) -> None:
        self.__token_name = token_name
        self.__token: str | None = None

    @property
    def token(self) -> str:
        return self.__token if self.__token is not None else utility.String.empty

    def load_token(self) -> bool:
        try:
            import pyenv
            self.__token = pyenv.environ.get(self.__token_name)
        except KeyError:
            import os
            import dotenv
            dotenv.load_dotenv()
            self.__token = os.environ.get(self.__token_name)

        return self.__token is not None and self.__token is not None
