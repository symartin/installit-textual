import dataclasses
import os
import time
import traceback
import subprocess
import shutil
import requests
import git
from git.repo import Repo

from typing import TYPE_CHECKING, Type
from multiprocessing import Process, Pipe, Queue
from multiprocessing.connection import Connection
from pathlib import Path


from .optclass import OptInfo

__all__ = ["InstallWorker", "InstallWorker", "InstallAction", "ProcessInfo"]

_GIT_OP_CODES = [
    "BEGIN",
    "CHECKING_OUT",
    "COMPRESSING",
    "COUNTING",
    "END",
    "FINDING_SOURCES",
    "RECEIVING",
    "RESOLVING",
    "WRITING",
]

_GIT_OP_CODE_MAP = {
    getattr(git.RemoteProgress, _op_code): _op_code for _op_code in _GIT_OP_CODES
}


@dataclasses.dataclass(frozen=True, eq=True)
class InstallAction:
    """ a dataclass to hold installation action information """
    name: str
    opt_name:str
    description: str
    message: str = ''
    has_progress: bool = False


class InstallWorker:
    """
    the worker will update messages to the ``pipe`` connection, in the form of 
    tuple(str, obj). the str being the command and the obj being the object of 
    this command.


    =============== ============================================================ 
    command            description
    =============== ============================================================ 
    'action'        a new action is started, the action is describe by an
                    ``Action`` object
    'progress'      update the progress bar, the obj the percentage in ``float``
    'done'          the worker is finished, the obj is ``None``
    'error'         an error occurred, the obj is the error ``str`` description
    'start'         the worker is started, the obj is ``None``
    =============== ============================================================ 

    :param pipe: the Pipe connection to communicate with the main thread/process
    :param option_obj: the option object to be installed
    """

    def __init__(self, queue: Queue, opt_info: OptInfo):  # type: ignore
        self._queue = queue
        self.opt_info: OptInfo = opt_info

    def _clone_git(self) -> None:
        """
        Clones the git repositories specified in opt_info.repos.
        """
        def progress_report(op_code, cur_count, max_count=None, message=''):
            self._queue.put(('progress', cur_count/max_count*100))

            op_nme = _GIT_OP_CODE_MAP.get(op_code, "").title()
            self._queue.put(('message_update', f"{op_nme} {message}"))

        if not self.opt_info.repos:
            return

        for repo in self.opt_info.repos:

            self._queue.put(
                ('action',
                 InstallAction(
                     name="Git cloning",
                     opt_name=self.opt_info.name,
                     description=repo.url,
                     has_progress=True,
                     message='Preparing...'))
            )

            try:
                # create the path tree if not exists
                # it is simpler to eventual create the last directory
                # even if we remove it latter
                Path(repo.path).mkdir(parents=True, exist_ok=True)

                # delete the target directory if it exists
                shutil.rmtree(repo.path)

            # pylint: disable=bare-except
            except:
                self._queue.put(('error', traceback.format_exc()))

            multi_options = ['--recurse-submodules'] if repo.submodule else []
            Repo.clone_from(
                repo.url,
                repo.path,
                multi_options=multi_options,
                progress=progress_report)

            # to avoid github ban ...
            time.sleep(0.5)

    def _file_download(self) -> None:
        """
        Downloads files from `opt_info.files` and saves them locally.
        """

        if not self.opt_info.files:
            return

        for file in self.opt_info.files:
            self._queue.put(
                ('action',
                 InstallAction(
                     name="Downloading",
                     opt_name=self.opt_info.name,
                     description=file.url,
                     has_progress=True,
                     message=file.url))
            )
                        
            try:
                response = requests.get(file.url, stream=True)
                response.raise_for_status()
                total_size = int(response.headers['Content-Length'])
                
                Path(os.path.dirname(file.path)).mkdir(parents=True, exist_ok=True)
                
                # create the path tree if not exists
                with open(file.path, 'wb') as file:
                    downloaded_size = 0
                    for data in response.iter_content(total_size//50):
                        file.write(data)
                        downloaded_size += len(data)
                        progress = (downloaded_size / total_size) * 100
                        self._queue.put(('progress', progress))

            except FileNotFoundError as e:
                self._queue.put(("error", "cannot access remote file"))

            except BrokenPipeError:
                pass

            except OSError as e:
                self._queue.put(("error", "cannot access local file"))

    def _exec_shell_cmd(self) -> None:
        """
        This method is called internally to execute the shell
        commands provided in the `opt_info` `cmd` list.
        """
        if not self.opt_info.cmd:
            return

        for cmd in self.opt_info.cmd:

            self._queue.put(
                ('action',
                 InstallAction(
                     name="Execute command",
                     opt_name=self.opt_info.name,
                     description=cmd,
                     has_progress=False))
            )

            subprocess.Popen(cmd, shell=True)

    def run(self) -> None:
        """ start the worker."""

        if self._queue is None:
            raise RuntimeError("pipe_connection is not set")

        self._queue.put(('start', None))

        self._clone_git()

        self._file_download()

        self._exec_shell_cmd()

        self._queue.put(('done', None))


@dataclasses.dataclass(frozen=True, eq=True)
class ProcessInfo:
    worker: InstallWorker
    process: Process
    queue: Queue
    opt: OptInfo


def piped_process_factory(opt: OptInfo) -> ProcessInfo:
    """
    Create a InstallWorker and start it in a process.

    :param opt: The OptInfo to be install 
    :return: return ProcessInfo dataclass
    """

    parent_conn, child_conn = Pipe()
    q = Queue()
    worker = InstallWorker(q, opt)
    process = Process(target=worker.run)
    process.start()

    return ProcessInfo(worker, process, q, opt)
