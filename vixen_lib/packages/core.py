"""
Author            : Nohavye
Author's Email    : noha.poncelet@gmail.com
Repository        : https://github.com/vixen-shell/vixen-environment.git
Description       : vixen packages management.
License           : GPL3
"""

from typing import Optional, Callable, List
from subprocess import run, PIPE
from .status import StatusHandler
from ..tools import cli

SUCCES_MESSAGE = cli.TypedMessage('succes').success
FAILURE_MESSAGE = cli.TypedMessage('failure').failure

class Requirement:
    def __init__(
        self,
        purpose: str,
        callback: Callable[[], bool],
        failure_details: Optional[str|None] = None
    ) -> None:
        self.__purpose = purpose
        self.__callback = callback
        self.__failure_details = failure_details

    def __show_message_check_up(self, success: bool) -> None:
        if success: print(cli.MessageCheckUp(self.__purpose).success)
        else: print(cli.MessageCheckUp(self.__purpose).failure)

    def __show_failure_details(self) -> None:
        if self.__failure_details:
            print(
                f"\n{cli.TypedMessage('Requirements are not satisfied').failure} : {self.__failure_details}."
            )

    def isSatisfied(self) -> bool:
        result = self.__callback()
        self.__show_message_check_up(result)
        if not result: self.__show_failure_details()
        return result
    
class Requirements:
    def __init__(
        self,
        requirements: List[Requirement] = []
    ) -> None:
        self.__requirements = requirements

    def check(self) -> bool:
        value = True

        for requirement in self.__requirements:
            result = requirement.isSatisfied()
            if value: value = result

        return value
    
class Task:    
    def __init__(
            self,
            purpose: str,
            process_command: str,
            requirements: Requirements = Requirements()
    ) -> None:
        self.__purpose = purpose
        self.__process_command = process_command
        self.__requirements = requirements
        self.__done = False
    
    @property
    def done(self) -> bool:
        return self.__done
    
    def __show_message_check_up(self, success: bool) -> None:
        if success: print(cli.MessageCheckUp(self.__purpose).success)
        else: print(cli.MessageCheckUp(self.__purpose).failure)

    def __process(self) -> bool:
        result = cli.run(self.__process_command)
        self.__show_message_check_up(result)
        if result: self.__done = True

        return result
        
    def run(self) -> bool:
        requirements = self.__requirements.check()
        return self.__process() if requirements else False

def requirements_builder(requirements_data: Optional[List[dict]|None]) -> Requirements:
    if not requirements_data: return Requirements()
    
    requirement_list: List[Requirement] = []

    for requirement in requirements_data:
        requirement_list.append(Requirement(
            purpose=requirement['purpose'],
            callback=requirement['callback'],
            failure_details=requirement.get('failure_details')
        ))

    return Requirements(requirement_list)

def task_builder(task_data: dict) -> Task:
    return Task(
        purpose=task_data['purpose'],
        process_command=task_data['process_command'],
        requirements=requirements_builder(task_data.get('requirements'))
    )

class Setup:
    def __init__(self, setup_data: dict) -> None:
        self.__task_list: List[Task] = []
        self.__purpose: str = setup_data['purpose']
        print(f'\n{cli.TypedMessage(self.__purpose).title}\n')
        
        self.__init_status(setup_data.get('status'))
        self.__init_tasks(setup_data['tasks'])

    def __init_status(self, new_data: Optional[dict|None]):
        self.__status = StatusHandler(new_data)

        if not self.__status.init(): self.__finalize(False)

    def __init_tasks(self, tasks_data: List[dict]):

        for task_data in tasks_data:
            self.__task_list.append(task_builder(task_data))
    
    @property
    def __has_done_tasks(self) -> bool:
        for task in self.__task_list:
            if task.done: return True

        return False
    
    def process(self) -> None:
        for task in self.__task_list:
            if not task.run(): self.__finalize(False)

        self.__finalize()

    def __finalize(self, success: bool = True) -> None:
        self.__status.finalize(success, self.__has_done_tasks)

        if success:
            print(cli.TypedMessage('\nExecution was successful!').success)
            exit(0)
        else:
            print(cli.TypedMessage('\nExecution failed!').failure)
            exit(1)
