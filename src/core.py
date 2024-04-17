class Core:
    def __init__(self, token_name: str) -> None:
        self.__token_var_name = token_name
        self.__token: str = ''

    @property
    def token(self) -> str:
        return self.__token

    def load_environ(self) -> bool:
        '''
        トークンを読み込めたらtrue
        '''
        try:
            import pyenv
            self.__token = pyenv.environ[self.__token_var_name]
        except KeyError:
            import os
            import dotenv
            dotenv.load_dotenv()
            self.__token = os.environ[self.__token_var_name]
        return self.__token is not None and len(self.__token) > 0
