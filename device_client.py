import asyncio
import json
import os

import websockets
from websockets.legacy import client

from adds import SendRequest


class WServer(SendRequest):
    security_key = os.getenv('SECURITY_KEY')
    device_id = os.getenv('DEVICE_ID')
    port = os.getenv('PORT', 443)
    uri = f"{'wss' if port in ['443', 443] else 'ws'}://{os.getenv('HOST')}:{port}/device/{device_id}/?security_key={security_key}"
    websocket = client.WebSocketClientProtocol

    async def accepted(self):
        message = json.dumps({"text": "Hello from Python WebSocket client!"})
        await self.websocket.send(message)

    async def receive(self, data: dict):
        if data.pop('type') == 'send_request':
            res = await self.send_request(data)
            await self.websocket.send(json.dumps(res))

    async def connect_to_server(self):
        async with websockets.connect(self.uri) as websocket:
            self.websocket = websocket

            await self.accepted()

            async for message in websocket:
                await self.receive(json.loads(message))

    def start(self):
        asyncio.run(self.connect_to_server())


if __name__ == "__main__":
    server = WServer()
    server.start()
