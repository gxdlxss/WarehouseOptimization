import asyncio
import websockets
import json
import random
from websockets.asyncio.server import ServerConnection
from websockets.exceptions import ConnectionClosedOK

connected_clients = set()


async def server_handler(websocket: ServerConnection) -> None:
    connected_clients.add(websocket)
    print(f"Клиент {websocket.id} подключился")
    try:
        asyncio.create_task(send_on_condition(websocket))

        async for message in websocket:
            data = json.loads(message)
            print(data)

            """
            response = {
                "status": "ok",
                "received": data,
                "message": "Сообщение обработано сервером!"
            }
            await websocket.send(json.dumps(response))
            """

    except ConnectionClosedOK:
        print(f"Клиент {websocket.id} отключился до завершения сессии")
    finally:
        connected_clients.remove(websocket)


async def send_on_condition(websocket: ServerConnection) -> None:
    while True:
        try:
            try:
                random_number = random.random()

                if random_number > 0.9:
                    message = {
                        "type": "server_update",
                        "random_number": random_number,
                        "data": "Условие выполнено! Отправляем сообщение."
                    }
                    await websocket.send(json.dumps(message))
                    print(f"Сервер отправил сообщение: {message}")
            except ConnectionClosedOK:
                print(f"Клиент {websocket.id} отключился")
                break

            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Ошибка при отправке сообщений: {e}")
