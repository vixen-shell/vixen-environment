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

SNAPSHOTS_PARENT_DIRECTORY = '/var/opt/vixen/snapshots'

def snapshot_builder(status: dict) -> SnapShot:
    entries = [status['env_path']]

    for path in status['exec_paths']:
        entries.append(path)

    return SnapShot(SNAPSHOTS_PARENT_DIRECTORY, entries)

class StatusHandler:
    def __init__(self, data: dict) -> None:
        self.__initial = data.pop('initial') if 'initial' in data else False
        self.__new_data = data
        self.__current_status = None
        self.__snapshot = None

    def init(self) -> bool:
        if self.__initial: return self.__init_for_initial()
        if not self.__read(): return False
        self.__snapshot = snapshot_builder(self.__current_status)
        if not self.__snapshot.create(): return False
        return True

    def __init_for_initial(self) -> bool:
        return True

    def __read(self) -> bool:
        purpose = 'Read packages status'
        data = read()

        if not data:
            print(cli.MessageCheckUp(purpose).failure)
            self.__current_status = None
            return False

        print(cli.MessageCheckUp(purpose).success)
        self.__current_status = data
        self.__new_data['exec_paths'].extend(data['exec_paths'])
        return True
    
    def __update(self) -> bool:
        purpose = 'Update package status'
        callback = create if self.__initial else update

        if not callback(self.__new_data):
            print(cli.MessageCheckUp(purpose).failure)
            return False

        print(cli.MessageCheckUp(purpose).success)
        return True
    
    def __clean_new_exec(self) -> bool:
        for path in self.__new_data['exec_paths']:
            if not path in self.__current_status['exec_paths']:
                if fs.exists(path):
                    if fs.remove(path): print(cli.MessageCheckUp(f"Remove {path}").success)
                    else: print(cli.MessageCheckUp(f"Remove {path}").failure)

    def finalize(self, success: bool, restore: bool) -> None:
        if not success:
            if restore:
                self.__clean_new_exec()
                if self.__snapshot: self.__snapshot.restore()
        else:
            self.__update()
        
        if self.__snapshot: self.__snapshot.remove()