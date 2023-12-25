"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen packages management.
License           : GPL3
"""

from typing import Optional, Callable, List
from .state import PackagesState
from ..tools import cli

class Requirement:
    def __init__(
        self,
        purpose: str,
        callback: Callable[[], bool],
        failure_msg: Optional[str|None] = None
    ) -> None:
        self._purpose = purpose
        self._callback = callback
        self._failure_msg = failure_msg

    def _show_check_msg(self, success: bool) -> None:
        msg = cli.CheckMsg(self._purpose)
        print(msg.success if success else msg.failure)

    def _show_failure_msg(self) -> None:
        prompt = cli.TypedMsg('Requirements are not satisfied').failure
        msg = f" : {self._failure_msg}" if self._failure_msg else ''
        print(f"\n{prompt}{msg}")

    def is_satisfied(self) -> bool:
        result = self._callback()
        self._show_check_msg(result)
        if not result: self._show_failure_msg()
        return result

def data_to_requirements(
    requirements_data: Optional[List[dict]|None]
) -> List[Requirement]:
    if not requirements_data: return []

    return [
        Requirement(
            purpose=data['purpose'],
            callback=data['callback'],
            failure_msg=data.get('failure_details')
        ) for data in requirements_data
    ]

class Task:    
    def __init__(
            self,
            purpose: str,
            cmd: str,
            requirements: List[Requirement] = []
    ) -> None:
        self._purpose = purpose
        self._cmd = cmd
        self._requirements = requirements
        self._is_done = False
    
    @property
    def is_done(self) -> bool:
        return self._is_done
    
    def _show_check_msg(self, success: bool) -> None:
        msg = cli.CheckMsg(self._purpose)
        print(msg.success if success else msg.failure)

    def _check_requirements(self) -> bool:
        return all(
            requirement.is_satisfied() for requirement in self._requirements
        )

    def _process(self) -> bool:
        self._is_done = cli.run(self._cmd)
        self._show_check_msg(self._is_done)
        return self._is_done
        
    def run(self) -> bool:
        return self._process() if self._check_requirements() else False

def data_to_task(task_data: dict) -> Task:
    return Task(
        purpose=task_data['purpose'],
        cmd=task_data['process_command'],
        requirements=data_to_requirements(task_data.get('requirements'))
    )

class Setup:
    def __init__(self, data: dict) -> None:
        self._tasks: List[Task] = []
        self._purpose: str = data['purpose']

        print(f'\n{cli.TypedMsg(self._purpose).title}\n')
        
        self._init_state(data.get('state'))
        self._init_tasks(data['tasks'])

    def _init_state(self, new_data: Optional[dict|None]):
        self._packages_state = PackagesState(new_data)
        if not self._packages_state.init(): self._finalize(False)
        if not self._packages_state.create_snapshot(): self._finalize(False)

    def _init_tasks(self, tasks_data: List[dict]):
        self._tasks = [data_to_task(data) for data in tasks_data]
    
    @property
    def _has_done_tasks(self) -> bool:
        return any(task.is_done for task in self._tasks)
    
    def process(self) -> None:
        result = not any(not task.run() for task in self._tasks)
        self._finalize(result)

    def _finalize(self, success: bool) -> None:
        self._packages_state.finalize(success, self._has_done_tasks)

        msg = cli.CheckMsg('Execution')
        print(msg.success if success else msg.failure)
        exit(0 if success else 1)
