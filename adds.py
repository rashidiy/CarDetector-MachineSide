import base64
import os
import os.path
import subprocess

import requests
from requests.auth import HTTPDigestAuth


def create_service_file(service_name, file_path, device_id, security_key, host, port, description='Device',
                        python_path='/usr/bin/python3'):
    service_path = f'/etc/systemd/system/{service_name}.service'
    try:
        with open('template.txt') as template_file:
            template = template_file.read()
        with open(service_path, 'w') as service_file:
            service_file.write(template.format(
                description=description,
                python_path=python_path,
                file_path=os.path.abspath(file_path),
                environment=f'"DEVICE_ID={device_id}" "SECURITY_KEY={security_key}" "HOST={host}" "PORT={port}"',
            ))
        enable_service(service_name)
        start_service(service_name)
        print(f"Service file {service_path} created successfully.")
    except IOError as e:
        print(f"Failed to create service file {service_path}: {e}")


def reload_daemon():
    try:
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        print("Systemd daemon reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reload systemd daemon: {e}")


def enable_service(service_name):
    try:
        subprocess.run(['sudo', 'systemctl', 'enable', service_name], check=True)
        print(f"Service {service_name} enabled successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to enable {service_name}: {e}")


def start_service(service_name):
    try:
        subprocess.run(['sudo', 'systemctl', 'start', service_name], check=True)
        print(f"Service {service_name} started successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to start {service_name}: {e}")


def stop_service(service_name):
    try:
        subprocess.run(['sudo', 'systemctl', 'stop', service_name], check=True)
        print(f"Service {service_name} stopped successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to stop {service_name}: {e}")


def delete_service(file_path):
    try:
        subprocess.run(['rm', '-rf', file_path], check=True)
        print(f"Service {file_path} deleted successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to delete {file_path}: {e}")
    reload_daemon()


class SendRequest:

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
