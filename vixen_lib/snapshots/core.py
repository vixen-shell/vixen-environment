"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen snapshots feature.
License           : GPL3
"""

from typing import List
from datetime import datetime
from ..tools import fs, cli

SUCCES_MESSAGE = cli.TypedMessage('succes').success
FAILURE_MESSAGE = cli.TypedMessage('failure').failure

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
            if not self.__snap.create_parent_directory(): return False

        return self.__original.copy(
            to=self.__snap.parent_directory
        )
    
    def restore(self) -> bool:
        if not self.__snap.exists: return False
        if not self.__original.remove(): return False

        return self.__snap.copy(
            to=self.__original.parent_directory
        )
    
class SnapShot:
    def __init__(self, parent_directory: str, entries: List[str]) -> None:
        self.__snaps: List[Snap] = []
        self.__snapshot_directory = fs.File(
            name=datetime.now().strftime("%Y%m%d_%H%M%S"),
            parent_directory=parent_directory,
            file_type=fs.FileType.DIRECTORY
        )        
        self.__snapshot_directory.create()

        if self.__snapshot_directory.exists:
            for entry in entries:
                self.__snaps.append(Snap(entry, self.__snapshot_directory.path))

    def create(self) -> bool:
        purpose = 'Create snapshot'
        for snap in self.__snaps:
            if not snap.create():
                print(cli.MessageCheckUp(purpose).failure)
                return False

        print(cli.MessageCheckUp(purpose).success)
        return True
    
    def restore(self) -> bool:
        purpose = 'Restore snapshot'
        for snap in self.__snaps:
            if not snap.restore():
                print(cli.MessageCheckUp(purpose).failure)
                return False

        print(cli.MessageCheckUp(purpose).success)
        return True
    
    def remove(self) -> bool:
        purpose = 'Remove Snapshot'
        if not self.__snapshot_directory.remove():
            print(cli.MessageCheckUp(purpose).failure)
            return False

        print(cli.MessageCheckUp(purpose).success)
        return True