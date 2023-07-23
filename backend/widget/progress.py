
from typing import Optional
from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Static, Label,  ProgressBar

from backend.worker import InstallAction





class ProgressWidget(Static):

    """
    A widget that represents a progress bar and the current action name
    a description, and a message.
    
    for example: the action can be 'Git cloning' the description the
    git repository url and the message the file currently being cloned.
    
    TODO: add a progress bar visual state for undefined progress
    """

    DEFAULT_CSS = """
    ProgressWidget {
        height: 4;
        width: auto;
        padding: 0 0 1 0
        
    }
    ProgressBar{
        height: 1;
    }
    
    #action_name{
        height: 1;
        padding: 0 1 0 0
    }
    
    #action_desc{
        content-align: center top;
        padding: 0 1 0 0
    }
    
    #action_msg{
        content-align: center top;
        padding: 0 1 0 0
    }
    """

    def __init__(
            self,
            name: Optional[str] = None,
            id: Optional[str] = None,
            classes: Optional[str] = None,
            disabled: bool = False) -> None:

        super().__init__(name=name, id=id, classes=classes, disabled=disabled)

        self._action_name_lbl = Label("Preparing...", id="action_name")
        self._action_desc_lbl = Label("Preparing the installation...", id="action_desc")
        self._action_msg_lbl = Label(" ", id="action_msg")
        self._progress_bar = ProgressBar(
            total=100, show_eta=False, id="progress_bar")

        self._has_progress = False

    def set_starting(self) -> None:
        """ set the widget to a preparing state """
        self.has_progress = False
        self._action_name_lbl.update("Preparing...")
        self._action_desc_lbl.update("Preparing the installation...")
        self._action_msg_lbl.update(" ")
    
    def set_finished(self) -> None:
        """ set the widget to a finished state """
        self.has_progress = True
        self._progress_bar.update(progress=100)
        self._action_name_lbl.update("Done...")
        self._action_desc_lbl.update("Installation finished...")
        self._action_msg_lbl.update(" ")
        
        
    def compose(self) -> ComposeResult:
        with Vertical(id="vertical"):
            with Horizontal():
                yield self._action_name_lbl
                yield self._progress_bar

            yield self._action_desc_lbl
            yield self._action_msg_lbl

    def set_progress(self, progress: Optional[int]) -> None:
        """ 
        Updates the progress bar with the given progress value.
        if None the progress bar is set to an undefined progress
        
        :param progress: the progress value between 0 and 100
        """
        if progress is not None:
            self._progress_bar.update(progress=progress)
        else:
            self._has_progress = False

    @property
    def has_progress(self) -> bool:
        """ if the widget has an active progress bar """
        return self._has_progress

    @has_progress.setter
    def has_progress(self, has_progress: bool) -> None:
        self._has_progress = has_progress
        self._progress_bar.show_percentage = has_progress
        if has_progress:
            self._progress_bar.update(progress=0)
        else:
            self._progress_bar.update(progress=None)
            

    def set_action(self, action:InstallAction) -> None:
        """ Updates the action name and action description 
        labels with the given values."""
        
        self._action_name_lbl.update(action.name)
        self._action_desc_lbl.update(action.description)
        self.has_progress = action.has_progress
        
    def set_message(self, message: str) -> None:
        """ Sets the message label str. """
        self._action_msg_lbl.update(message)
        
