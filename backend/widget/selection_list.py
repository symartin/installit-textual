from typing import Optional
from rich.segment import Segment
from textual.strip import Strip
from rich.style import Style

from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import (SelectionList, Markdown)
from textual.containers import VerticalScroll
from textual import on
from textual.events import Mount

from ..optclass import OptInfo

class OptionSelectionList(SelectionList[OptInfo]):
    """Custom selection list with a clearer visual selection."""

    BUTTON_LEFT: str = "▐"
    """The character used for the left side of the toggle button."""

    BUTTON_INNER_OFF: str = "-"
    """The character used for the inside of the button."""

    BUTTON_INNER_ON: str = "X"
    """The character used for the inside of the button."""

    BUTTON_RIGHT: str = "▌"
    """The character used for the right side of the toggle button."""

    def render_line(self, y: int) -> Strip:
        """Render a line in the display.

        Args:
            y: The line to render.

        Returns:
            A [`Strip`][textual.strip.Strip] that is the line to render.
        """

        # First off, get the underlying prompt from OptionList.
        prompt = super().render_line(y)

        # If it looks like the prompt itself is actually an empty line...
        if not prompt:
            # ...get out with that. We don't need to do any more here.
            return prompt

        # We know the prompt we're going to display, what we're going to do
        # is place a CheckBox-a-like button next to it. So to start with
        # let's pull out the actual Selection we're looking at right now.
        _, scroll_y = self.scroll_offset
        selection_index = scroll_y + y
        selection = self.get_option_at_index(selection_index)

        # Figure out which component style is relevant for a checkbox on
        # this particular line.
        component_style = "selection-list--button"
        if selection.value in self._selected:
            component_style += "-selected"
        if self.highlighted == selection_index:
            component_style += "-highlighted"

        # Get the underlying style used for the prompt.
        underlying_style = next(iter(prompt)).style
        assert underlying_style is not None

        # Get the style for the button.
        button_style = self.get_component_rich_style(component_style)

        # If the button is in the unselected state, we're going to do a bit
        # of a switcharound to make it look like it's a "cutout".
        if selection.value not in self._selected:
            button_style += Style.from_color(
                self.background_colors[1].rich_color, button_style.bgcolor # type: ignore
            )

        # Build the style for the side characters. Note that this is
        # sensitive to the type of character used, so pay attention to
        # BUTTON_LEFT and BUTTON_RIGHT.
        side_style = Style.from_color(button_style.bgcolor, underlying_style.bgcolor)

        inner = self.BUTTON_INNER_OFF if selection.value not in self._selected else self.BUTTON_INNER_ON

        # At this point we should have everything we need to place a
        # "button" before the option.
        return Strip(
            [
                Segment(self.BUTTON_LEFT, style=side_style),
                Segment(inner, style=button_style),
                Segment(self.BUTTON_RIGHT, style=side_style),
                Segment(" ", style=underlying_style),
                *prompt.crop(4),
            ]
        )


class MarkdownScrollable(VerticalScroll, can_focus=True):
    """A Markdown viewer widget."""

    DEFAULT_CSS = """
    MarkdownScrollable {
        scrollbar-gutter: stable;
        background: $boost;
        color: $text;
        padding: 0 1 1 1; 
        border: tall transparent;
        
    }
    
    MarkdownScrollable:focus {
        border: tall $accent;

    }

    Markdown {
        overflow-y: hidden;
    }
    """

    def __init__(
        self,
        markdown: Optional[str] = None,
        *,
        name: Optional[str] = None,
        id: Optional[str] = None,
        classes: Optional[str] = None,
    ):
        """ Create a Markdown scrollable viewier.

        :param markdown: String containing Markdown, or None to leave blank.
        :param name: The name of the widget.
        :param id: The ID of the widget in the DOM.
        :param classes: The CSS classes of the widget.

        """
        super().__init__(name=name, id=id, classes=classes)
        self._markdown = markdown

    @property
    def document(self) -> Markdown:
        """The Markdown document object."""
        return self.query_one(Markdown)

    @document.setter
    def document(self, document: str):
        self._markdown = document
        self.query_one(Markdown).update(document)

    def _on_mount(self, _: Mount) -> None:
        if self._markdown is not None:
            self.document.update(self._markdown)

    def compose(self) -> ComposeResult:
        yield Markdown()


class OptSelection(Widget):
    """ compound widget with a selection list of option and a description field
    the user can select option to install. 

    :param options: a list of ``OptInfo`` options to show in the list
    :param name: The name of the widget.
    :param id: The ID of the widget in the DOM.
    :param classes: The CSS classes for the widget.
    :param disabled: Whether the widget is disabled or not.

    """
    DEFAULT_CSS = """
    OptSelection {
        layout: horizontal;
        height: 100vh;
        padding: 0 3 3 1;
    }
    
    MarkdownScrollable {
        width: 65%;
        height: 75%;
    }
    
    OptionSelectionList {
        height: 75%;
        width: 35%;
        overflow-y: scroll !important; 
        padding: 0 1 1 1; 
        scrollbar-gutter: stable;
    }
    
    """

    # pylint: disable=too-many-arguments, disable=redefined-builtin
    def __init__(self, options: list[OptInfo], name: Optional[str] = None,
                 id: Optional[str] = None, classes: Optional[str] = None,
                 disabled: bool = False) -> None:

        super().__init__(name=name, id=id, classes=classes, disabled=disabled)
        self._options = options

        self._list_wgt = OptionSelectionList(
            *list((opt.name, opt, opt.default) for opt in self._options),
            id="opt_list")
        
        self._description_mrk = MarkdownScrollable(
            "### Description: \n\n ", id="description",
            classes="description")

    def compose(self) -> ComposeResult:
        yield self._list_wgt
        yield self._description_mrk

    @on(Mount)
    @on(SelectionList.SelectionHighlighted, "#opt_list")
    def update_opt_description(self) -> None:
        """ update the description label according to the opt highlighted. """
        idx = self._list_wgt.highlighted
        if idx is not None:
            self._description_mrk.document.update("### Description: \n\n " + self._options[idx].description)

    @property
    def selection(self) -> list[OptInfo]:
        """ Return the list of selected Option. """
        return self._list_wgt.selected
