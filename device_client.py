import asyncio
import base64
import json
import os

import requests
import websockets
from requests.auth import HTTPDigestAuth
from websockets.legacy import client


class WServer:
    security_key = os.getenv('SECURITY_KEY')
    device_id = os.getenv('DEVICE_ID')
    port = os.getenv('PORT', 443)
    uri = f"{'wss' if port == 443 else 'ws'}://{os.getenv('HOST')}:{port}/device/{device_id}/?security_key={security_key}"
    websocket = client.WebSocketClientProtocol

    async def accepted(self):
        message = json.dumps({"text": "Hello from Python WebSocket client!"})
        await self.websocket.send(message)

    async def send_request(self, data):
        auth_credits = data.pop('auth')
        match auth_credits.get('type'):
            case 'digest':
                auth = HTTPDigestAuth(auth_credits.get('username'), auth_credits.get('password'))
            case _:
                auth = None
        status_code = -1
        content = None
        response_channel = None
        if 'response_channel' in data:
            response_channel = data.pop('response_channel')
        try:
            req = requests.Request(**data, auth=auth).prepare()
            with requests.Session() as session:
                res = session.send(req, timeout=100)
            status_code = res.status_code
            text = res.text
            content = base64.b64encode(res.content).decode('utf-8') if 'cgi' in data.get(
                'url') or 'picture' in data.get('url') else None
        except requests.exceptions.Timeout:
            text = "The request timed out"
        except requests.exceptions.RequestException as e:
            text = f"An error occurred: {e}"

        return {
            'status_code': status_code,
            'text': text,
            'response_channel': response_channel,
            'content': content
        }

    async def receive(self, data: dict):
        print(data)
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
