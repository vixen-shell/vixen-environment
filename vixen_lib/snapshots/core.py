"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen snapshots management.
License           : GPL3
"""

from typing import List
from datetime import datetime
from ..tools import fs

class Snap:
    def __init__(self, origin_path: str, snapshot_path: str) -> None:
        self.__origin = fs.PathEntry(origin_path)
        self.__snap = fs.PathEntry(
            f'{snapshot_path}{self.__origin.parent_path}/{self.__origin.entry}'
        )

    def create(self) -> bool:
        if not fs.exists(self.__snap.parent_path):
            if not fs.create_folder(
                path=self.__snap.parent_path,
                sudo=True
            ): return False

        return fs.copy(
            path=self.__origin.path,
            to=self.__snap.parent_path,
            sudo=True
        )
    
    def restore(self) -> bool:
        if not fs.remove(
            path=self.__origin.path,
            sudo=True
        ): return False

        return fs.copy(
            path=self.__snap.path,
            to=self.__origin.parent_path,
            sudo=True
        )
    
class SnapShot:
    def __init__(self, parent_path: str, entries: List[str]) -> None:
        self.__path_entry = fs.PathEntry(f'{parent_path}/{datetime.now().strftime("%Y%m%d_%H%M%S")}')
        self.__snaps: List[Snap] = []

        for entry in entries:
            self.__snaps.append(Snap(entry, self.__path_entry.path))

    def create(self) -> bool:
        if not fs.exists(self.__path_entry.parent_path):
            if not fs.create_folder(
                path=self.__path_entry.parent_path,
                sudo=True
            ): return False

        for snap in self.__snaps:
            if not snap.create(): return False

        return True
    
    def restore(self) -> bool:
        for snap in self.__snaps:
            if not snap.restore(): return False

        return True
    
    def remove(self) -> bool:
        return fs.remove(self.__path_entry.path, sudo=True)