"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen packages management.
License           : GPL3
"""

from typing import Optional, Callable, List
from subprocess import run, PIPE
from ..tools import cli
from ..snapshots import SnapShot

SUCCES_MESSAGE = cli.TypedMessage('succes').success
FAILURE_MESSAGE = cli.TypedMessage('failure').failure

class Requirement:
    def __init__(
        self,
        purpose: str,
        callback: Callable[[], bool],
        failure_details: Optional[str|None] = None
    ) -> None:
        self.purpose = purpose
        self.__callback = callback
        self.failure_details = failure_details

    def isSatisfied(self) -> None:
        return self.__callback()
    
class Requirements:
    def __init__(
        self,
        requirements: List[Requirement] = []
    ) -> None:
        self.__requirements = requirements

    def check(self) -> bool:
        value = True

        for requirement in self.__requirements:
            if not requirement.isSatisfied():
                print(f'{requirement.purpose} : {FAILURE_MESSAGE}')

                if requirement.failure_details:
                    print(
                        f"\n{cli.TypedMessage('Execution failed').failure} : {requirement.failure_details}."
                    )

                if value: value = False
            else:
                print(f'{requirement.purpose} : {SUCCES_MESSAGE}')

        return value
    
class Task:    
    def __init__(
            self,
            purpose: str,
            process_command: str,
            cancel_command: Optional[str|None] = None,
            requirements: Requirements = Requirements()
    ) -> None:
        self.__purpose = purpose
        self.__process_command = process_command
        self.__cancel_command = cancel_command
        self.__requirements = requirements
        self.__cancellable = False

    def __handle_purpose(self, cancel: bool) -> str:
        prefix = '' if not cancel else cli.TypedMessage('Cancel ').warning
        return (prefix + self.__purpose)

    def __process(self, cancel: bool = False):
        command = self.__process_command if not cancel else self.__cancel_command

        if run(command, shell=True, stdout=PIPE).returncode == 0:
            print(f'{self.__handle_purpose(cancel)} : {SUCCES_MESSAGE}')
            if self.__cancel_command: self.__cancellable = True
            return True
        else:
            print(f'{self.__handle_purpose(cancel)} : {FAILURE_MESSAGE}')
            return False
        
    def run(self) -> bool:
        if not self.__requirements.check(): return False
        else: return self.__process()

    def cancel(self) -> bool:
        return self.__process(cancel=True)
    
    @property
    def cancellable(self) -> bool:
        return self.__cancellable
    
class Setup:
    def __init__(self, setup_data: dict) -> None:
        self.__purpose: str = setup_data['purpose']
        self.__task_list = []

        for task_data in setup_data['tasks']:
            self.__task_list.append(self.__task_builder(task_data))

    def __requirements_builder(self, requirements_data: Optional[List[dict]|None]) -> Requirements:
        if not requirements_data: return Requirements()
        
        requirement_list: List[Requirement] = []

        for requirement in requirements_data:
            requirement_list.append(Requirement(
                purpose=requirement['purpose'],
                callback=requirement['callback'],
                failure_details=requirement.get('failure_details')
            ))

        return Requirements(requirement_list)
    
    def __task_builder(self, task_data: dict) -> Task:
        return Task(
            purpose=task_data['purpose'],
            process_command=task_data['process_command'],
            cancel_command=task_data.get('cancel_command'),
            requirements=self.__requirements_builder(task_data.get('requirements'))
        )
    
    def process(self) -> None:
        print(f'\n{cli.TypedMessage(self.__purpose).title}\n')

        for task in self.__task_list:
            if not task.run():
                self.__cancel_process()
                exit(1)

        print(cli.TypedMessage('\nExecution was successful!').success)

    def __cancel_process(self) -> None:
        print()

        for task in reversed(self.__task_list):
            if task.cancellable: task.cancel()