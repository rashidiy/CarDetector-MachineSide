import asyncio
import json
import os

import websockets as ws
from dotenv import load_dotenv

from adds import create_service_file

load_dotenv()


class CompanyConsumer:
    company_id: str = os.getenv('COMPANY_ID')
    security_key: str = os.getenv('SECURITY_KEY')
    host: str = os.getenv('HOST')
    port: int = os.getenv('PORT', 80)
    url: str = f'ws://{host}:{port}/company/{company_id}/?security_key={security_key}'
    websocket: ws.WebSocketClientProtocol

    async def accepted(self):
        message = json.dumps({"text": "Hello from Python WebSocket client!"})
        await self.websocket.send(message)

    async def receive(self, data: dict):
        print(data)
        if data.get('type') == 'company.new_device':
            datas = data.get('data')
            create_service_file(
                service_name=datas.get('id').replace('-', '_'),
                description=datas.get('name'),
                file_path='device_client.py',
                device_id=datas.get('id'),
                security_key=datas.get('security_key'),
                host=os.getenv('HOST'),
                port=os.getenv('PORT'),
                python_path='/home/rashidiy/.cache/pypoetry/virtualenvs/cardetector-Vt2OEhlt-py3.12/bin/python3'
            )
        if data.get('type') == 'send_request':
            await self.websocket.send(json.dumps({'ok': True}))

    async def connect(self):
        async with ws.connect(self.url) as websocket:
            self.websocket = websocket
            await self.accepted()
            async for message in websocket:
                await self.receive(json.loads(message))

    def main(self):
        return asyncio.new_event_loop().run_until_complete(self.connect())


if __name__ == '__main__':
    CompanyConsumer().main()
