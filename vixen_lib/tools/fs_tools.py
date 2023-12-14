"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen cli tools.
License           : GPL3
"""

import os
from . import cli

def exists(path: str) -> bool:
    return os.path.exists(path)

def is_file(path: str) -> bool:
    return os.path.isfile(path)

def create_file(
    path: str,
    outputs: cli.Outputs = {'out': False, 'err': True},
    sudo: bool = False
) -> bool:
    return cli.run(f'touch {path}', outputs, sudo)

def is_folder(path: str) -> bool:
    return os.path.isdir(path)

def create_folder(
    path: str,
    outputs: cli.Outputs = {'out': False, 'err': True},
    sudo: bool = False
) -> bool:
    return cli.run(f'mkdir -p {path}', outputs, sudo)

def copy(
    path: str,
    to: str,
    outputs: cli.Outputs = {'out': False, 'err': True},
    sudo: bool = False
) -> bool:
    option = '-r ' if os.path.isdir(path) else ''
    return cli.run(f'cp {option}{path} {to}', outputs, sudo)

def remove(
    path: str,
    outputs: cli.Outputs = {'out': False, 'err': True},
    sudo: bool = False
) -> bool:
    option = '-r ' if os.path.isdir(path) else ''
    return cli.run(f'rm {option}{path}', outputs, sudo)

class PathEntry:
    def __init__(self, path: str) -> None:
        segments = path.rsplit('/', 1)

        parent_path, entry = segments

        self.path = path
        self.parent_path = parent_path
        self.entry = entry