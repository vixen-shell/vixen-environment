from typing import List, Optional
from ..tools import fs, json, cli
from ..snapshots import SnapShot

STATUS_PATH = {
    'parent_directory': '/var/opt/vixen',
    'file_name': 'package_status.json'
}
STATUS_PATH['path'] = f"{STATUS_PATH['parent_directory']}/{STATUS_PATH['file_name']}"

def exists() -> bool:
    return fs.exists(STATUS_PATH['path'])

def create(data: dict) -> bool:
    if not fs.create(
        path=STATUS_PATH['parent_directory'],
        file_type=fs.FileType.DIRECTORY
    ): return False

    return json.create(
        path=STATUS_PATH['path'],
        data=data
    )

def update(data: dict) -> bool:
    if not exists(): return False
    return json.update(
        path=STATUS_PATH['path'],
        data=data
    )

def read() -> dict|None:
    if not exists(): return None
    return json.read(STATUS_PATH['path'])

def combine_unique_elements(a_list: List[str], b_list: List[str]) -> List[str]:
    unique_elements_b = [item for item in b_list if item not in a_list]
    unique_elements_a = [item for item in a_list if item not in b_list]
    
    result = unique_elements_b + unique_elements_a
    return result


SNAPSHOTS_PARENT_DIRECTORY = '/var/opt/vixen/snapshots'

def snapshot_builder(status: dict) -> SnapShot:
    entries = [status['env_path']]

    for path in status['exec_paths']:
        entries.append(path)

    return SnapShot(SNAPSHOTS_PARENT_DIRECTORY, entries)

class StatusHandler:
    def __init__(self, data: Optional[dict|None] = None) -> None:
        self.__new_data = data
        self.__current_status = None
        self.__snapshot = None

    def init(self) -> bool:
        if not self.__current_status_exists: return True
        if not self.__read_current_status(): return False
        return self.__create_snapshot()
    
    def __create_snapshot(self) -> bool:
        self.__snapshot = snapshot_builder(self.__current_status)
        return self.__snapshot.create()

    def __restore_snapshot(self) -> None:
        self.__clean_new_exec()
        if self.__snapshot: self.__snapshot.restore()

    def __remove_snapshot(self) -> None:
        if self.__snapshot: self.__snapshot.remove()

    def __clean_new_exec(self) -> None:
        if not self.__new_data: return

        for path in self.__new_data['exec_paths']:
            if not path in self.__current_status['exec_paths']:
                if fs.exists(path):
                    if fs.remove(path): print(cli.MessageCheckUp(f"Remove {path}").success)
                    else: print(cli.MessageCheckUp(f"Remove {path}").failure)

    @property
    def __current_status_exists(self) -> bool:
        return exists()

    def __read_current_status(self) -> bool:
        purpose = 'Read packages status'
        data = read()

        if not data:
            print(cli.MessageCheckUp(purpose).failure)
            return False

        print(cli.MessageCheckUp(purpose).success)
        self.__current_status = data
        return True
    
    def __update_status(self) -> bool:
        if not self.__new_data: return True

        purpose = 'Update package status'
        data = self.__new_data

        if not self.__current_status_exists:
            callback = create
        else:
            callback = update
            data['exec_paths'] = combine_unique_elements(
                data['exec_paths'], self.__current_status['exec_paths']
            )

        if not callback(data):
            print(cli.MessageCheckUp(purpose).failure)
            return False

        print(cli.MessageCheckUp(purpose).success)
        return True

    def finalize(self, success: bool, restore: bool) -> None:
        if not success and restore: self.__restore_snapshot()
        if success: self.__update_status()
        self.__remove_snapshot()