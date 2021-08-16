import asyncio
import websockets
from websockets import WebSocketServerProtocol
from jsonrpcserver import method, Success, Result


class Server:
    clients = set()

    @method
    async def sendEcho() -> Result:
        return Success("Message for me")

    async def register(self, ws:WebSocketServerProtocol) -> None:
	    self.clients.add(ws)
	  
    async def unregister(self, ws:WebSocketServerProtocol) -> None:
	    self.clients.remove(ws)

    @method
    async def sendMessage(self, message: str) -> Result:
        if self.clients:
            await asyncio.wait([client.send(message) for client in self.clients])
        return Success("Hello to all")

    async def ws_handler(self, ws: WebSocketServerProtocol, uri: str) -> None:
	    await self.register(ws)
	    try:
                await self.distribute(ws)
	    finally: 
                await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            await self.sendMessage(message)


server = Server()
start_server = websockets.serve(server.ws_handler,'localhost',5000)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()


