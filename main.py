import asyncio
import json
import os

import websockets as ws
from dotenv import load_dotenv

from adds import create_service_file, enable_service, start_service, SendRequest, delete_service

load_dotenv()


class CompanyConsumer(SendRequest):
    company_id: str = os.getenv('COMPANY_ID')
    security_key: str = os.getenv('SECURITY_KEY')
    host: str = os.getenv('HOST')
    port: int = os.getenv('PORT', 443)
    url: str = f'{'wss' if port in ['443', 443] else 'ws'}://{host}:{port}/company/{company_id}/?security_key={security_key}'
    websocket: ws.WebSocketClientProtocol

    async def accepted(self):
        message = json.dumps({"text": "Hello from Python WebSocket client!"})
        await self.websocket.send(message)

    async def new_device(self, data):
        datas = data.get('data')
        service_name = f'dev_{datas.get('id').replace('-', '_')}'
        create_service_file(
            service_name=service_name,
            description=datas.get('name'),
            file_path='device_client.py',
            device_id=datas.get('id'),
            security_key=datas.get('security_key'),
            host=self.host,
            port=self.port,
            python_path=os.getenv('PY_PATH')
        )
        enable_service(service_name)
        start_service(service_name)

    @staticmethod
    async def delete_device(data: dict):
        device_id = data.get('data', {}).get('id', '').replace('-', '_')
        delete_service(f'/etc/systemd/system/dev_{device_id}.service')

    async def receive(self, data: dict):
        match data.pop('type'):
            case 'company.new_device':
                await self.new_device(data)
            case 'company.delete_device':
                await self.delete_device(data)
            case 'send_request':
                res = await self.send_request(data)
                await self.websocket.send(json.dumps(res))

    async def connect(self):
        async with ws.connect(self.url) as websocket:
            self.websocket = websocket
            await self.accepted()
            async for message in websocket:
                data = json.loads(message)
                await self.receive(data)

    def main(self):
        return asyncio.run(self.connect())


if __name__ == '__main__':
    CompanyConsumer().main()
