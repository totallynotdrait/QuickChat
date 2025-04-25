# QuickChat Web Server

import asyncio
import websockets

PORT = 8765
connected_users = {}  # {websocket: username}

async def handler(websocket, path=None):  # Rendi 'path' opzionale
    try:
        username = await websocket.recv()
        connected_users[websocket] = username

        join_msg = f"[Server]: {username} joined the chat."
        print(join_msg)
        await broadcast(join_msg)

        async for message in websocket:
            await broadcast(f"{username}: {message}")

    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        if websocket in connected_users:
            left_msg = f"[Server]: {connected_users[websocket]} left the chat."
            print(left_msg)
            await broadcast(left_msg)
            del connected_users[websocket]

async def broadcast(message):
    for user in connected_users:
        try:
            await user.send(message)
        except:
            pass  # Handle send errors gracefully

async def main():
    async with websockets.serve(handler, "localhost", PORT):  # ✅ correct usage
        print(f"WebSocket server running on ws://localhost:{PORT}")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())