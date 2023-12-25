from typing import List, Optional, Callable
from ..tools import fs, json, cli
from ..snapshots import SnapShot

STATUS_PATH = {
    'parent_directory': '/var/opt/vixen',
    'file_name': 'package_status.json'
}
STATUS_PATH['path'] = f"{STATUS_PATH['parent_directory']}/{STATUS_PATH['file_name']}"
SNAPSHOTS_PARENT_DIRECTORY = '/var/opt/vixen/snapshots'

def exists() -> bool:
    return fs.exists(STATUS_PATH['path'])

def create_directory() -> bool:
    return fs.create(
        path=STATUS_PATH['parent_directory'],
        file_type=fs.FileType.DIRECTORY
    )

def create(data: dict) -> bool:
    if not create_directory(): return False
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

def combine_list(a_list: List[str], b_list: List[str]) -> List[str]:
    ele_b = [item for item in b_list if item not in a_list]
    ele_a = [item for item in a_list if item not in b_list]
    return ele_b + ele_a

def snapshot_builder(status: dict) -> SnapShot:
    entries = [status['env_path']] + status['exec_paths']
    return SnapShot(SNAPSHOTS_PARENT_DIRECTORY, entries)

class PackagesState:
    class Purpose:
        INIT: str = 'Initializing packages state'
        CHECK_STATE_INI: str = 'Check if packages state does not exists'
        CHECK_STATE_SUB: str = 'Check if packages state exists'
        LOAD_STATE: str = 'Load packages state'
        UPDATE_STATE: str = 'Update packages state'
        CREATE_SNAPSHOT: str = 'Create snapshot'
        RESTORE_SNAPSHOT: str = 'Restore snapshot'
        REMOVE_SNAPSHOT: str = 'Remove snapshot'

    def __init__(self, data: Optional[dict|None] = None) -> None:
        self._initial_state = False

        if data:
            if data.get('env_path'): self._initial_state = True

        self._new_data = data
        self._current_state = None
        self._snapshot = None

    def _show_check_msg(self, purpose: str, success: bool) -> None:
        msg = cli.CheckMsg(purpose)
        print(msg.success if success else msg.failure)

    def _show_msg(self, purpose: str, detail_message: str = '') -> None:
        if detail_message != '':
            purpose = f"{purpose} : "
            detail_message = cli.TypedMsg(detail_message).warning

        print(purpose + detail_message)

    def init(self) -> bool:
        purpose = self.Purpose.INIT

        if not self._check_state_availability():
            self._show_check_msg(purpose, False)
            return False
        
        if not self._initial_state:
            if not self._load_state():
                self._show_check_msg(purpose, False)
                return False

        self._show_check_msg(purpose, True)
        return True
    
    def _check_state_availability(self) -> bool:
        purpose = self.Purpose.CHECK_STATE_SUB
        result = exists()

        if self._initial_state:
            purpose = self.Purpose.CHECK_STATE_INI
            result = not result

        self._show_check_msg(purpose, result)
        return result
    
    def _load_state(self) -> bool:
        purpose = self.Purpose.LOAD_STATE
        data = read()

        if not data:
            self._show_check_msg(purpose, False)
            return False

        self._show_check_msg(purpose, True)
        self._current_state = data
        return True
        
    def create_snapshot(self) -> bool:
        purpose = self.Purpose.CREATE_SNAPSHOT

        if self._initial_state:
            self._show_msg(purpose, 'skipped')
            return True

        self._snapshot = snapshot_builder(self._current_state)
        return self._snapshot.create()

    def restore_snapshot(self) -> bool:
        purpose = self.Purpose.RESTORE_SNAPSHOT

        if not self._snapshot:
            self._show_msg(purpose, 'no snapshot')
            return True
        
        self._clean_new_exec()
        return self._snapshot.restore()

    def remove_snapshot(self) -> bool:
        purpose = self.Purpose.REMOVE_SNAPSHOT

        if not self._snapshot:
            self._show_msg(purpose, 'no snapshot')
            return True

        return self._snapshot.remove()

    def _clean_new_exec(self) -> None:
        if not self._new_data or self._initial_state:
            return

        for path in self._new_data['exec_paths']:
            if path not in self._current_state['exec_paths'] and fs.exists(path):
                result = fs.remove(path)
                self._show_check_msg(f"Remove {path}", result)
    
    def update_state(self) -> bool:
        purpose = self.Purpose.UPDATE_STATE
        
        if not self._new_data:
            self._show_msg(purpose, 'no update data')
            return True

        data = self._new_data

        if self._initial_state:
            callback = create
        else:
            callback = update
            data['exec_paths'] = combine_list(
                data['exec_paths'], self._current_state['exec_paths']
            )

        if not callback(data):
            self._show_check_msg(purpose, False)
            return False

        self._show_check_msg(purpose, True)
        return True

    def finalize(self, success: bool, restore: bool) -> None:
        if not success and restore: self.restore_snapshot()
        if success: self.update_state()
        self.remove_snapshot()