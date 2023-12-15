"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen file system tools.
License           : GPL3
"""

import os
from . import cli
from enum import Enum
from typing import Optional

class FileType(Enum):
    FILE = 'file'
    DIRECTORY = 'directory'

def exists(path: str) -> bool:
    return os.path.exists(path)

def is_file(path: str) -> bool:
    return os.path.isfile(path)

def is_directory(path: str) -> bool:
    return os.path.isdir(path)

def get_file_type(path: str) -> FileType:
    if is_file(path): return FileType.FILE
    if is_directory(path): return FileType.DIRECTORY

def create(
    path: str,
    file_type: FileType = FileType.FILE,
    outputs: cli.Outputs = {'out': False, 'err': True},
    sudo: bool = False
) -> bool:
    
    if file_type == FileType.FILE:
        return cli.run(f'touch {path}', outputs, sudo)

    if file_type == FileType.DIRECTORY:
        return cli.run(f'mkdir -p {path}', outputs, sudo)

def copy(
    path: str,
    to: str,
    outputs: cli.Outputs = {'out': False, 'err': True},
    sudo: bool = False
) -> bool:
    option = '-r ' if is_directory(path) else ''
    return cli.run(f'cp {option}{path} {to}', outputs, sudo)

def remove(
    path: str,
    outputs: cli.Outputs = {'out': False, 'err': True},
    sudo: bool = False
) -> bool:
    option = '-r ' if is_directory(path) else ''
    return cli.run(f'rm {option}{path}', outputs, sudo)

class File:
    def __init__(
        self,
        path: Optional[str|None] = None,
        name: Optional[str|None] = None,
        parent_directory: Optional[str|None] = None,
        file_type: Optional[FileType|None] = None
    ) -> None:
        
        if path:
            self.path = path
            self.name = os.path.basename(path)
            self.parent_directory = os.path.dirname(path)
            self.file_type = get_file_type(path)
        else:
            self.path = f'{parent_directory}/{name}'
            self.name = name
            self.parent_directory = parent_directory
            self.file_type = file_type

    @property
    def exists(self) -> bool:
        return exists(self.path)
    
    @property
    def parent_directory_exists(self) -> bool:
        return exists(self.parent_directory)
    
    def create(
        self,
        outputs: cli.Outputs = {'out': False, 'err': True},
        sudo: bool = False
    ) -> bool:
        return create(
            self.path,
            self.file_type,
            outputs,
            sudo
        )
    
    def create_parent_directory(
        self,
        outputs: cli.Outputs = {'out': False, 'err': True},
        sudo: bool = False
    ) -> bool:
        return create(
            self.parent_directory,
            FileType.DIRECTORY,
            outputs,
            sudo
        )
    
    def copy(
        self,
        to: str,
        outputs: cli.Outputs = {'out': False, 'err': True},
        sudo: bool = False
    ) -> bool:
        return copy(
            self.path,
            to,
            outputs,
            sudo
        )
    
    def remove(
        self,
        outputs: cli.Outputs = {'out': False, 'err': True},
        sudo: bool = False
    ) -> bool:
        return remove(
            self.path,
            outputs,
            sudo
        )