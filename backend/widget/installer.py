
import time
from typing import Optional
from textual import work

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widget import Widget
from textual.widgets import TextLog
from textual.timer import Timer
from multiprocessing import Process
from multiprocessing.connection import Connection

from ..optclass import OptInfo

from backend.widget import ProgressWidget
from backend import ProcessInfo, piped_process_factory


MAX_WORKERS = 3


class InstallerWidget(Widget):

    DEFAULT_CSS = """
    InstallerWidget {
        layout: vertical;
        height: 100%;
        # padding: 0 1 1 1; 

    }
    # ProgressWidget{
    #     height: 3;
    # }
    
    #progress_layout{
        background: $boost;
        margin: 1 1 0 1; 
        padding: 0 1 0 1; 
        border-bottom: tall $boost;
        height: 1fr;
    }
    
    TextLog {
        margin: 1 0 0 0; 
        background: $boost;
        padding: 0 2 0 2; 
        height: 1fr;
    }    
    """

    def __init__(
            self,
            name: Optional[str] = None,
            id: Optional[str] = None, classes:
            Optional[str] = None) -> None:

        super().__init__(name=name, id=id, classes=classes)

        self._text_log = TextLog(id="text_log", highlight=True, markup=True)

        self._progress_widgets: list[ProgressWidget] = \
            [ProgressWidget(id=f"progress_{i}") for i in range(MAX_WORKERS)]

        self._is_running = False
        self._process_pool: list[ProcessInfo] = []
        self._remaining_work: list[OptInfo] = []
        self._group_name: str = ""

    async def on_mount(self) -> None:
        # cannot put it in __init__, because the event loop is not started yet
        self._update_timer: Timer = self.set_interval(
            1 / 100, callback=self._pool_manager, pause=True)

    def compose(self) -> ComposeResult:
        with Vertical():
            with Vertical(id="progress_layout"):
                for wgt in self._progress_widgets:
                    yield wgt

            yield self._text_log

    def _pool_manager(self):

        if (len(self._remaining_work) + len(self._process_pool)) == 0:
            self._post_install()
            return

        try:
            if len(self._process_pool) < MAX_WORKERS and len(self._remaining_work):
                opt = self._remaining_work.pop(0)

                self._process_pool.append(piped_process_factory(opt))

            self._handle_installer_messages()

        except KeyboardInterrupt:
            for prc in self._process_pool:
                prc.process.terminate()
                prc.process.join()

            raise
        self.refresh()

    def _post_install(self):
        self._update_timer.pause()
        self._is_running = False
        for w in self._progress_widgets:
            w.set_finished()

        self._text_log.write(f"[bold magenta]{self._group_name}: Installation finished")

    def _pre_install(self):
        for w in self._progress_widgets:
            w.set_starting()
        self._is_running = True

        self._text_log.write(f"[bold magenta]{self._group_name}: Preparing the installation")

    def _handle_installer_messages(self):
        for i, prc in enumerate(self._process_pool):
            if not prc.queue.empty():
                cmd, obj = prc.queue.get()

                if cmd == "done":
                    # type: obj:None
                    prc.process.join()
                    self._progress_widgets[i].set_finished()
                    self._process_pool.pop(i)
                    self._text_log.write(f"[bold green]{prc.opt.name}  Install is completed")

                elif cmd == "error":
                    # type: obj:str
                    prc.process.join()
                    self._process_pool.pop(i)
                    self._text_log.write(f"[bold red]{prc.opt.name}: Error: {obj}")

                elif cmd == "progress":
                    # type: obj:int
                    self._progress_widgets[i].set_progress(obj)

                elif cmd == 'action':
                    # type: obj:InstallAction
                    self._progress_widgets[i].set_action(obj)
                    self._text_log.write(f"{obj.opt_name}: {obj.name}: {obj.description}")

                elif cmd == "start":
                    # type: obj:None
                    self._progress_widgets[i].set_starting()
                    self._text_log.write(f"[bold green]{prc.opt.name}: Installation is starting")
                    
                elif cmd == "message_update":
                    # type: obj:str
                    self._progress_widgets[i].set_message(obj)

    def install(self, group_name: str, opt_list: list[OptInfo]) -> None:
        self._group_name = group_name
        self._process_pool: list[ProcessInfo] = []
        self._remaining_work: list[OptInfo] = opt_list.copy()

        self._pre_install()
        self._update_timer.resume()

    @property
    def is_running(self) -> bool:
        return self._is_running

    def _update_progress(self) -> None:
        if self._is_running:
            pass
