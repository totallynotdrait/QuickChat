![immagine](https://github.com/user-attachments/assets/e327525f-6e73-464d-9591-f807009e38d2)


# QuickChat
An easy-to-use server and client for local chatting with Python Socket or with Web Socket

Both Python Socket and Web Socket servers are written in Python

This repository includes a client to connect Python Socket or Web Socket server

# Installation
### Server
- Clone repository `https://github.com/totallynotdrait/QuickChat`
- To start a Python Socket do `python server.py`, it will start on a local IP server (127.0.0.1) on port 12345
- To start a Web Socket do `python webserver.py`, it will start a server at `wb://localhost:8765`

### Client
The included client is built with [Textual](https://github.com/Textualize/textual), it provides basic connection to Python Socket or Web Socket servers

# Planned changes
- Improved server interface with [Textual](https://github.com/Textualize/textual)
- Commands for Server Admin (kick, mute, announce, lsclient, ...)
- Full Web Socket implementation
- Run server in web (for example https://totallynotdrait.github.io/proj/QuickChat/test-server)
