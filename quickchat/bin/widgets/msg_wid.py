from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Label
from textual.containers import ScrollableContainer
from textual import on
from textual.widgets._list_item import ListItem

from datetime import datetime
import re


def replace_links(text):
    url_pattern = r'(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+)'
    replacement = r'[@click="app.open_link(\'\1\')"]\1[/]'
    new_text = re.sub(url_pattern, replacement, text)
    return new_text


class MessageEntry(Label):
    def __init__(self, message) -> None:
        self.message = message
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(self.message, expand=True)

class ConnectedOnServer(ScrollableContainer):
    def compose(self) -> ComposeResult:
        yield Label("\nConnected to server:")
        yield Label("hello wqoeeq")


class ServerMessageEntry(ListItem):
    def compose(self) -> ComposeResult:
        now = datetime.now()
        time_now = now.strftime("%H:%M:%S")

        date = now.strftime("%Y/%m/%d")
        yield Label("[dark_orange][Server][/dark_orange]"+f"        [bright_black]{date} | {time_now}[/bright_black]"+"\n"+self.message)

class MessageView(ScrollableContainer):
    def __init__(self, *children: Widget, name: str | None = None, id: str | None = None, classes: str | None = None, disabled: bool = False) -> None:
        self.last_time = None
        self.last_username = None
        super().__init__(*children, name=name, id=id, classes=classes, disabled=disabled)

    def _scroll_to_bottom(self):
        self.scroll_end(animate=False)

    def write_onview(self, username, msg):
        now = datetime.now()
        time_now = now.strftime("%H:%M:%S")
        time_hm = now.strftime("%H:%M")
        date = now.strftime("%Y/%m/%d")
        msg = replace_links(msg)

        if time_hm != self.last_time or username != self.last_username:
            self.mount(MessageEntry(f"[bold mediumpurple]{username}[/bold mediumpurple]      [darkgrey]{date} | {time_now}[/darkgrey]\n{msg}"))
            self.last_time = time_hm
            self.last_username = username
        else:
            self.mount(MessageEntry(msg))

        self.call_later(self._scroll_to_bottom)

    def write_onview_server(self, msg):
        now = datetime.now()
        time_now = now.strftime("%H:%M:%S")
        date = now.strftime("%Y/%m/%d")
        msg = replace_links(msg)

        self.mount(MessageEntry(f"[bold orange]\[Server][/bold orange]      [darkgrey]{date} | {time_now}[/darkgrey]\n{msg}"))
        self.call_later(self._scroll_to_bottom)

    def write_error(self, msg):
        msg = replace_links(msg)

        self.mount(MessageEntry(f"[bold red]\[Error][/bold red] {msg}\n"))
        self.call_later(self._scroll_to_bottom)
    
    

