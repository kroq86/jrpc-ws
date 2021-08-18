import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol
from jsonrpcserver import method, Success, Result, async_dispatch

logging.basicConfig(level=logging.INFO)

class Server:

    clients = set()
        
    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info("connects")
        print(self.clients)

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info("disconnects")

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            logging.info("send")
            await asyncio.wait([client.send(message) for client in self.clients])

    async def ws_handler(self, ws: WebSocketServerProtocol) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        for message in ws:
            asyncio.create_task(self.send_to_clients(message))
            logging.info("send")


server = Server()


@method
async def sendEcho() -> Result:
    return Success("Echo Message")            


@method
async def checkAndSend() -> Result:
    await server.ws_handler('localhost')
    return Success("Hi there")  


async def main(websocket, path):
    if response := await async_dispatch(await websocket.recv()):
        await websocket.send(response)


start_server = websockets.serve(main,'localhost',5000)
loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()
