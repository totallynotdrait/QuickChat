# QuickChat Server

import socket
import threading

# setup
AF = socket.AF_INET  # Use socket.AF_INET for IPv4
HOST = "192.168.1.237"
PORT = 12345  # Use a different port number
LISTENER_LIMIT = 13
MESSAGE_LIMIT = 2048

active_clients = []  # list of all connected clients

def listen_for_messages(client, username):
    while True:
        try:
            response = client.recv(MESSAGE_LIMIT).decode("utf-8")
            if response:
                final_msg = f"{username}[pls_no_write] {response}"
                send_message_to_all(final_msg)
            else:
                print(f"{username} disconnected")
                client.close()

                active_clients.remove((username, client))
                send_message_to_all(f"[Server]: [bold]{username}[/] left the chat.")
                break
        except Exception as e:
            print(f"An error occurred with client {username}: {e}")
            client.close()
            if (username, client) in active_clients:
                active_clients.remove((username, client))
            send_message_to_all(f"{username} left the chat.")
            break

def send_message_to_client(client, message):
    client.sendall(message.encode())

def send_message_to_all(message):
    for user in active_clients:
        send_message_to_client(user[1], message)

def client_handler(client):
    while True:
        username = client.recv(MESSAGE_LIMIT).decode('utf-8')
        if username:
            active_clients.append((username, client))
            prm_msg = f"[Server]: {username} joined the chat."
            print(prm_msg)
            send_message_to_all(f"[bold]{username}[/] joined the chat.")
            break
        else:
            print("Empty username is not valid!")

    threading.Thread(target=listen_for_messages, args=(client, username)).start()

def main():
    server = socket.socket(AF, socket.SOCK_STREAM)

    try:
        server.bind((HOST, PORT))
        print(f"Running server on {HOST}:{PORT}")
    except Exception as e:
        print(f"Unable to bind to host and port {HOST}:{PORT}: {e}")
        return

    server.listen()

    while True:
        client, address = server.accept()
        print(f"Client connected from {address[0]}:{address[1]}")
        threading.Thread(target=client_handler, args=(client,)).start()

if __name__ == "__main__":
    main()
