import asyncio
import websockets
from websockets import WebSocketServerProtocol


class Server:
    clients = set()

    async def register(self, ws:WebSocketServerProtocol) -> None:
	    self.clients.add(ws)
	  
    async def unregister(self, ws:WebSocketServerProtocol) -> None:
	    self.clients.remove(ws)

    async def sendMessage(self, message: str) -> None:
        message = "Hello to all"
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            await self.sendMessage(message)

    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
	    await self.register(ws)
	    try:
                await self.distribute(ws)
	    finally: 
                await self.unregister(ws)



server = Server()
start_server = websockets.serve(server.ws_handler,'localhost',5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
