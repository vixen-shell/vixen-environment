class TypedMessage:
    def __init__(self, message: str) -> None:
        self.__message = message

    @property
    def title(self) -> str:
        return f"\033[1;34m{self.__message}\033[0m"
    
    @property
    def success(self) -> str:
        return f"\033[32m{self.__message}\033[0m"
    
    @property
    def warning(self) -> str:
        return f"\033[33m{self.__message}\033[0m"

    @property
    def failure(self) -> str:
        return f"\033[31m{self.__message}\033[0m"