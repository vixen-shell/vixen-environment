"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen snapshots feature.
License           : GPL3
"""

from typing import List
from datetime import datetime
from ..tools import fs

class Snap:
    def __init__(self, original_path: str, snapshot_directory: str) -> None:
        self.__original = fs.File(original_path)
        self.__snap = fs.File(
            name=self.__original.name,
            parent_directory=f'{snapshot_directory}{self.__original.parent_directory}',
            file_type=self.__original.file_type
        )

    def create(self) -> bool:
        if self.__snap.exists: return False

        if not self.__snap.parent_directory_exists:
            if not self.__snap.create_parent_directory(sudo=True): return False

        return self.__original.copy(
            to=self.__snap.parent_directory,
            sudo=True
        )
    
    def restore(self) -> bool:
        if not self.__snap.exists: return False
        if not self.__original.remove(sudo=True): return False

        return self.__snap.copy(
            to=self.__original.parent_directory,
            sudo=True
        )
    
class SnapShot:
    def __init__(self, parent_directory: str, entries: List[str]) -> None:
        self.__snaps: List[Snap] = []
        self.__snapshot_directory = fs.File(
            name=datetime.now().strftime("%Y%m%d_%H%M%S"),
            parent_directory=parent_directory,
            file_type=fs.FileType.DIRECTORY
        )        
        self.__snapshot_directory.create(sudo=True)

        if self.__snapshot_directory.exists:
            for entry in entries:
                self.__snaps.append(Snap(entry, self.__snapshot_directory.path))

    def create(self) -> bool:
        for snap in self.__snaps:
            if not snap.create(): return False

        return True
    
    def restore(self) -> bool:
        for snap in self.__snaps:
            if not snap.restore(): return False

        return True
    
    def remove(self) -> bool:
        return self.__snapshot_directory.remove(sudo=True)