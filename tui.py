import socket
import threading
import logging
import asyncio
import websockets

from typing import Coroutine, Any
from textual.app import App
from textual.widgets import Input, Header, Footer, Label
from textual import on
from textual.binding import Binding
from quickchat.bin.widgets.msg_wid import MessageView

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MESSAGE_LIMIT = 2048



class QuickChat(App):
    CSS_PATH = "quickchat/bin/tcss/clt_sidebar.tcss"

    def __init__(self):
        super().__init__()
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_message_to_server(self, message: str):
        """Send message to server."""
        if message:
            try:
                self.client.sendall(message.encode())
                mv.write_onview(USERNAME, message)
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
                mv.write_error(f"Failed to send message: {e}\nServer may be down.")
        else:
            logger.warning("Empty message")

    def listen_for_messages_from_server(self):
        """Listen for messages from server."""
        #self.call_from_thread(mv.write_onview_server, "Listening for messages...")
        
        while True:
            try:
                data = self.client.recv(MESSAGE_LIMIT)
                if not data:
                    logger.warning("Server closed connection")
                    break
                message = data.decode("utf-8")
                # Check for delimiter
                if "[pls_no_write] " in message:
                    username, content = message.split("[pls_no_write] ", 1)
                    if username != USERNAME:
                        self.call_from_thread(mv.write_onview, username, content)
                    #logger.info("Message received from %s", username)
                else:
                    # System/server message
                    self.call_from_thread(mv.write_onview_server, message)
                    #logger.info("Server message: %s", message)
            except Exception as e:
                #logger.error(f"Error receiving message from server: {e}")
                # continue listening even if a message is malformed
                continue

    def communicate_to_server(self):
        """Communicate with the server."""
        #mv.write_onview_server("Communicating with server...")
        if not USERNAME:
            logger.error("Username is empty")
            exit(1)

        # Send username handshake so server can register this client
        try:
            self.client.sendall(USERNAME.encode('utf-8'))
        except Exception as e:
            logger.error(f"Failed to send username to server: {e}")
            exit(1)

        # Start thread to listen for incoming messages
        
        threading.Thread(target=self.listen_for_messages_from_server, daemon=True).start()

    def main(self):
        """Main function."""
        global mv
        mv = self.query_one(MessageView)

        try:
            self.sub_title = f"Connecting to {HOST}:{PORT}"
            self.client.connect((HOST, PORT))
            mv.write_onview_server("Connected to server")
            self.sub_title = f"Connected to {HOST}:{PORT}"
            self.communicate_to_server()
        except Exception as e:
            logger.error(f"Unable to connect to server {HOST}:{PORT}: {e}")
            exit(1)

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
        self.send_message_to_server(msg)
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
        yield Input(placeholder="Type message here...", max_length=MESSAGE_LIMIT)
        yield Label("")
        yield Footer()


class QuickChatWS(QuickChat):
    def __init__(self):
        super().__init__()
        self.ws = None

    async def send_message_to_server_ws(self, message: str):
        if message:
            try:
                await self.ws.send(message)
                mv.write_onview(USERNAME, message)
            except Exception as e:
                logger.error(f"Failed to send message via WebSocket: {e}")

    async def listen_for_messages_ws(self):
        try:
            async for message in self.ws:
                if "[pls_no_write] " in message:
                    username, content = message.split("[pls_no_write] ", 1)
                    if username != USERNAME:
                        self.call_from_thread(mv.write_onview, username, content)
                else:
                    self.call_from_thread(mv.write_onview_server, message)
        except Exception as e:
            logger.error(f"WebSocket listener error: {e}")
            mv.write_error(f"WebSocket listener error: {e}\nServer may be down.")

    async def main_ws(self):
        global mv
        mv = self.query_one(MessageView)

        try:
            self.ws = await websockets.connect(HOST)
            mv.write_onview_server("Connected to WebSocket server")
            self.sub_title = f"Connected to {HOST}"
            await self.ws.send(USERNAME)  # Handshake

            # Use Textual's safe background runner
            self.run_worker(self.listen_for_messages_ws, thread=False, exclusive=True)
        except Exception as e:
            logger.error(f"WebSocket connection failed: {e}")
            exit(1)

    @on(Input.Submitted)
    async def send_message(self, event):
        msg = event.value
        await self.send_message_to_server_ws(msg)
        self.query_one(Input).value = ""

async def mmain():
    global USERNAME, HOST, PORT
    logger.info("\nQuickChat Client\n==================================")
    qc_c_co = input("Connection options:\n[a] Global server\n[b] Local server\n[c] WebSocket\n[e] Exit\n(default: a)\n")
    
    if qc_c_co == "b":
        USERNAME = input("Enter username: ")
        HOST = input("Enter host: ")
        PORT = int(input("Enter port: "))
        app = QuickChat()
        app.call_after_refresh(app.main)
        await app.run_async()

    elif qc_c_co == "c":
        USERNAME = input("Enter username: ")
        HOST = input("Enter WebSocket URL (e.g. ws://localhost:8765): ")
        app = QuickChatWS()
        app.call_after_refresh(app.main_ws)
        await app.run_async()

    elif qc_c_co == "e":
        exit(0)

    else:
        USERNAME = input("Enter username: ")
        HOST, PORT = '127.0.0.1', 12345
        app = QuickChat()
        app.call_after_refresh(app.main)
        await app.run_async()

if __name__ == "__main__":
    asyncio.run(mmain())
