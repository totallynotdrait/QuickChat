# Quick Chat
# Experimental server with Textual as TUI
import socket
import threading
import asyncio

from typing import Coroutine, Any
from textual.app import App
from textual.widgets import Input, Header, Footer, Label
from textual import on
from textual.binding import Binding
from quickchat.bin.widgets.msg_wid import MessageView

AF = socket.AF_INET  # Use socket.AF_INET for IPv4
HOST = "192.168.1.237"
PORT = 12345  # Use a different port number
LISTENER_LIMIT = 13
MESSAGE_LIMIT = 2048

SET_VIEW_MESSAGES = False

active_clients = []  # list of all connected clients

class QuickChatServer(App):
    CSS_PATH = "quickchat/bin/tcss/clt_sidebar.tcss"

    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_shutdown_request(self, times, message):
        """Send shutdown request to server."""
        if message:
            try:
                message = f"The server will shutdown in T-{times} seconds, Reason: {message}"
                self.send_message_to_all(message)
                mv.write_onview_server(message)
            except Exception as e:
                mv.write_error(f"Failed to send message: {e}\nServer may be down.")

    
    def listen_for_messages(self, client, username):
        while True:
            try:
                response = client.recv(MESSAGE_LIMIT).decode("utf-8")
                if response:
                    final_msg = f"{username}[pls_no_write] {response}"
                    self.send_message_to_all(final_msg)
                else:
                    print(f"{username} disconnected")
                    client.close()

                    active_clients.remove((username, client))
                    self.send_message_to_all(f"[Server]: [bold]{username}[/] left the chat.")
                    break
            except Exception as e:
                client.close()
                if (username, client) in active_clients:
                    active_clients.remove((username, client))
                self.send_message_to_all(f"{username} left the chat.")
                self.call_from_thread(
                    mv.write_onview_server,
                    f"Client '{username}' disconnected"
                )
                break

    def send_message_to_client(self, client, message):
        client.sendall(message.encode())

    def send_message_to_all(self, message):
        for user in active_clients:
            self.send_message_to_client(user[1], message)

    def client_handler(self, client):
        while True:
            username = client.recv(MESSAGE_LIMIT).decode('utf-8')
            if username:
                active_clients.append((username, client))
                prm_msg = f"[Server]: {username} joined the chat."
                print(prm_msg)
                self.send_message_to_all(f"[bold]{username}[/] joined the chat.")
                break
            else:
                self.call_from_thread(
                    mv.write_error,
                    f"Attempted to connect with empty username"
                )

        threading.Thread(target=self.listen_for_messages, args=(client, username)).start()
        


    def start_server_thread(self):
        def server_thread():
            server = socket.socket(AF, socket.SOCK_STREAM)
            try:
                server.bind((HOST, PORT))
                print(f"Running server on {HOST}:{PORT}")
            except Exception as e:
                print(f"Unable to bind to host and port {HOST}:{PORT}: {e}")
                self.call_from_thread(
                    mv.write_error,
                    f"Unable to bind to host and port {HOST}:{PORT}: {e}"
                )
                return

            server.listen()
            self.call_from_thread(
                mv.write_onview_server,
                "You are connected to the server. You are now a root (Server Admin)\n[underline]Remember![/underline] You quit or close this window, the server will be closed too."
            )

            while True:
                client, address = server.accept()
                print(f"Client connected from {address[0]}:{address[1]}")
                self.call_from_thread(
                    mv.write_onview_server,
                    f"Client connected from {address[0]}:{address[1]}"
                )
                threading.Thread(target=self.client_handler, args=(client,), daemon=True).start()

        threading.Thread(target=server_thread, daemon=True).start()
        self.sub_title = f"Server at {HOST}:{PORT}"

    def main(self):
        """Main function."""
        global mv
        mv = self.query_one(MessageView)
        self.start_server_thread()

    def action_quit(self) -> Coroutine[Any, Any, None]:
        """Action to quit."""
        if self.client:
            self.client.close()
        return super().action_quit()

    @on(Input.Submitted)
    def send_message(self, event):
        """Send message event."""
        input_widget = self.query_one(Input)
        msg = input_widget.value
        self.send_shutdown_request(1, msg)
        input_widget.value = ""

    BINDINGS = [
        ("ctrl+b", "app.toggle_sidebar()", "Sidebar"),
        ("ctrl+s", "app.screenshot()", "Screenshot"),
        Binding("ctrl+q", "app.quit", "Quit", show=True),
    ]

    def compose(self):
        """Compose function."""
        yield Header(show_clock=True)
        yield MessageView()
        yield Input(placeholder="Type commands here...", max_length=2046)
        yield Label("")
        yield Footer()

async def mmain():
    app = QuickChatServer()
    app.title = "QuickChat Server"
    app.call_after_refresh(app.main)
    await app.run_async()

if __name__ == "__main__":
    asyncio.run(mmain())