import os
import time
from typing import Optional
from textual import work
from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import (
    Footer, Header, SelectionList,
    TabbedContent, TabPane,
    ContentSwitcher, Tabs,
    Tab)

from backend import  OptInfo
from backend import YamlConfigLoader
from backend.widget import SelectionList, OptSelection, InstallerWidget

SCRIPT_PATH = os.path.dirname(os.path.realpath(__file__))


_CSS_FORBIDDEN = ['!', '"', '#', '$', '%', '&', ',' '(', ')', '*', '+', 
                  ',', '-', '.', '/', ':', ';', '<', '=', '>', '?', '@',
                  '[', '\\', ']', '^', ',' '{', '|', '}', '~', " ", "\t"]


def _escape(txt:str)->str:
    """ Escapes special characters in a given string."""
    for c in _CSS_FORBIDDEN:
        txt = txt.replace(c, '_')
    return txt

class OtpApp(App):
    """ 
    Application entry point, called when the application is started.
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
        ("shift+a", "select_all", "Select all"),
        ("a", "select_all_in_tab", "Select all in tab"),
        ("shift+d", "deselect_all", "Deselect all"),
        ("d", "deselect_all_in_tab", "Deselect all in tab"),
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
        
        self._opt_selection: dict[str, OptSelection] = {}
        """ dictionary storing all the OptSelection widgets """
        
        self._tab_pan:dict[str, TabPane] = {}
        
        self._content_switcher = ContentSwitcher(
            id="content_switcher", initial="optlist_page" )
        self._tab_content = TabbedContent(id="optlist_page")
        self._installer = InstallerWidget(id="install_pages")

    def _make_tab(self, opt_list: list[OptInfo]) -> SelectionList:
        """ Generate a Tab object based on a list of BaseOpt objects. """
        return SelectionList[OptInfo](
            (opt.name, opt, opt.default) for opt in opt_list) # type: ignore

    def compose(self) -> ComposeResult:
        """ Yield child widgets for a container. """
        yield self._header
        yield self._footer
        with self._content_switcher:
            with self._tab_content:
                for key, opt in self.opt_dict.items():
                    self._tab_pan[key] = TabPane(key)
                    with self._tab_pan[key]:
                        self._opt_selection[key] = OptSelection(opt)
                        yield self._opt_selection[key]

            yield self._installer
            

    async def on_mount(self) -> None:
        """ Executed when the widget is created.     
        It focus the tabs when the app starts."""
        # self._content_switcher.current = "opt_pages"
        self.query_one("#optlist_page").focus()

    @work
    def action_next(self):
        """
        Performs the `next` action based on the current state of the application.
        """
        if self._installer.is_running:
            return
        
        elif self._content_switcher.current == "optlist_page":
            self._content_switcher.current = "install_pages" # type: ignore
            
            # Loop through the opt_selection items and install the selected options
            for key, w in self._opt_selection.items():
                if len(selection := w.selection):
                    self._installer.install(key, selection)
                    
                    # Wait until the installer is finished
                    while self._installer.is_running:
                        time.sleep(1)
                
        else:
            self._content_switcher.current = "optlist_page" # type: ignore
                
    
    def _get_active_tab(self)-> Optional[Tab]:
        """  Retrieve the active tab. """
        if self._content_switcher.current == "optlist_page":
            if (active := self._tab_content.active) != "":
                return self._tab_content.get_child_by_type(Tabs).active_tab
            
    def action_select_all_in_tab(self):
        """ Selects all elements in the active tab's selection. """
        if (active_tab := self._get_active_tab()):
                    self._opt_selection[active_tab.label_text].select_all()

          
    def action_select_all(self):
        """ Selects all elements """
        if self._content_switcher.current == "optlist_page":
            for selection in self._opt_selection.values():               
                    selection.select_all()
                     
    def action_deselect_all(self):
        """ Selects all elements in the active tab's selection. """
        if self._content_switcher.current == "optlist_page":
            for selection in self._opt_selection.values():               
                    selection.deselect_all()
                                     
    def action_deselect_all_in_tab(self):
        """ Deselects all options in the currently active tab. """
        if (active_tab := self._get_active_tab()):
                    self._opt_selection[active_tab.label_text].deselect_all()


if __name__ == "__main__":
    app = OtpApp()
    app.run()
