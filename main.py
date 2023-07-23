import os
import time
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import (
    Footer, Header, SelectionList,
    TabbedContent, TabPane,
    ContentSwitcher)

from backend import  OptInfo
from backend import YamlConfigLoader
from backend.widget import SelectionList, OptSelection, InstallerWidget

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))

class OtpApp(App):
    """ 
    A simple app to chose extensions and model
    for Automatic 1111 and install them. 
    """

    CSS = """
    TabPane {
        padding: 0 1 1 1;
    }
    
    InstallWidget{
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("n", "next", "Next"),
    ]

    TITLE = "Auto Installer"

    def __init__(self):

        self.opt_dict, self.cst_dict = YamlConfigLoader().load(SCRIPT_PATH + "/config")
        self.TITLE = self.cst_dict.get("$TITLE$", self.TITLE)
        super().__init__()

        self._header = Header(id='header')
        self._footer = Footer()
        self._main = Container(id='main')
        self._installer = InstallerWidget(id="install_pages")
        self._opt_selection: dict[str, OptSelection] = {}
        self._content_switcher = ContentSwitcher(
            id="content_switcher", initial="opt_pages" )
        


    def _make_tab(self, opt_list: list[OptInfo]) -> SelectionList:
        """ Generate a Tab object based on a list of BaseOpt objects. """
        return SelectionList[OptInfo]((opt.name, opt, opt.default) for opt in opt_list) # type: ignore

    def compose(self) -> ComposeResult:

        yield self._header
        yield self._footer
        with self._content_switcher:
            with TabbedContent(id="opt_pages"):
                for key, opt in self.opt_dict.items():
                    with TabPane(key):
                        self._opt_selection[key] = OptSelection(opt)
                        yield self._opt_selection[key]

            yield self._installer

    async def on_mount(self) -> None:
        """Focus the tabs when the app starts."""
        self.query_one("#opt_pages").focus()

    @work
    def action_next(self):
        
        if self._installer.is_running:
            return
        
        elif self._content_switcher.current == "opt_pages":
            
            self._content_switcher.current = "install_pages" # type: ignore
            
            for key, w in self._opt_selection.items():
                if len(selection := w.selection):
                    self._installer.install(key, selection)
                    while self._installer.is_running:
                        time.sleep(1)
                
        else:
            self.query_one("#content_switcher").current = "opt_pages" # type: ignore
            

if __name__ == "__main__":
    app = OtpApp()
    app.run()
