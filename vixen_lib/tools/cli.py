"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen command line interface tools.
License           : GPL3
"""

import subprocess
from typing import TypedDict

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
    
SUCCES_MESSAGE = TypedMessage('succes').success
FAILURE_MESSAGE = TypedMessage('failure').failure

class MessageCheckUp:
    def __init__(self, message: str) -> None:
        self.__message = message

    @property
    def success(self) -> str:
        return f"{self.__message} : {SUCCES_MESSAGE}"
    
    @property
    def failure(self) -> str:
        return f"{self.__message} : {FAILURE_MESSAGE}"

class Outputs(TypedDict):
    out: bool
    err: bool

def run(
    command: str,
    outputs: Outputs = {'out': False, 'err': True}
) -> bool:
    if subprocess.run(
        command,
        stdout=subprocess.PIPE if not outputs['out'] else None,
        stderr=subprocess.PIPE if not outputs['err'] else None,
        shell=True
    ).returncode == 0: return True
    return False