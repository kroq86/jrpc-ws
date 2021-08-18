import asyncio
import logging
import websockets
from websockets import WebSocketServerProtocol
import time
import threading
from jsonrpcserver import method, Success, Result, async_dispatch


logging.basicConfig(level=logging.INFO)


class Server:

    clients = set()
    logging.info(f'start')

    def __init__(self):
        logging.info(f'init')
        
    async def register(self, ws: WebSocketServerProtocol) -> None:
        self.clients.add(ws)
        logging.info(f'{ws.remote_address} connects')

    async def unregister(self, ws: WebSocketServerProtocol) -> None:
        self.clients.remove(ws)
        logging.info(f'{ws.remote_address} disconnects')

    async def send_to_clients(self, message: str) -> None:
        if self.clients:
            logging.info("send")
            await asyncio.wait([client.send(message) for client in self.clients])

    async def ws_handler(self, ws: WebSocketServerProtocol, url: str) -> None:
        await self.register(ws)
        try:
            await self.distribute(ws)
        finally:
            await self.unregister(ws)

    async def distribute(self, ws: WebSocketServerProtocol) -> None:
        async for message in ws:
            await self.send_to_clients(message)

@method
async def sendEcho() -> Result:
    return Success("Message for me")            

async def timerThread(server,counter):
    counter = 0
    while True:
        await checkAndSend(server,counter)
        print("do " + str(counter))
        time.sleep(5)
        counter = counter + 1

async def checkAndSend(server,counter):
    await server.send_to_clients("Hi there: " + str(counter))

def between_callback(server,counter):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(timerThread(server,counter))
    loop.close()


server = Server()
start_server = websockets.serve(server.ws_handler,'localhost',5000)
counter = 0 

threading.Thread(target=between_callback,args=(server,counter,)).start()

loop = asyncio.get_event_loop()
loop.run_until_complete(start_server)
loop.run_forever()
