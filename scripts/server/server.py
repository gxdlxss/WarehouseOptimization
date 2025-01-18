import asyncio
import websockets
import json
import random
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosed

from scripts.parsers.json_parser import ParserManager
from scripts.exceptions.json_parser_exceptions import ExecutionError

connected_clients = set()
manager = ParserManager()


async def server_handler(websocket: ServerConnection) -> None:
    connected_clients.add(websocket)
    print(f"Клиент {websocket.id} подключился")
    try:
        asyncio.create_task(send_server_status(websocket))

        async for message in websocket:
            data = json.loads(message)

            try:
                await manager.execute(data)
            except Exception as e:
                response = {
                    "type": "answer",
                    "status": "Internal Server Error",
                    "code": 500,
                    "message": e
                }
                await websocket.send(json.dumps(response))

    except ConnectionClosed:
        print(f"Клиент {websocket.id} отключился до завершения сессии")
    finally:
        connected_clients.remove(websocket)


async def send_server_status(websocket: ServerConnection) -> None:
    while True:
        try:
            data = await manager.execute({"type": "solve"})

            if data is None:
                await asyncio.sleep(0.1)
                continue

            message = {
                "type": "server_update",
                "body": data
            }
            await websocket.send(json.dumps(message))
            print(f"Сервер отправил сообщение: {message}")

        except ConnectionClosed:
            print(f"Клиент {websocket.id} отключился")
            break
        except Exception as e:
            print(f"Ошибка при отправке сообщения: {e}")
