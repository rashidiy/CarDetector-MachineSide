import os.path
import subprocess


def create_service_file(service_name, file_path, device_id, security_key, host, port, description='Device', python_path='/usr/bin/python3'):
    service_path = f'/etc/systemd/system/{service_name}.service'
    try:
        with open('template.txt') as template_file:
            template = template_file.read()
        print()
        print(template.format(
            description=description,
            python_path=python_path,
            file_path=os.path.abspath(file_path),
            environment=f'"DEVICE_ID={device_id}" "SECURITY_KEY={security_key}" "HOST={host}" "PORT={port}"',
        ))
        # with open(service_path, 'w') as service_file:
        #
        #
        #     service_file.write()
        print(f"Service file {service_path} created successfully.")
    except IOError as e:
        print(f"Failed to create service file {service_path}: {e}")


def reload_daemon():
    try:
        subprocess.run(['sudo', 'systemctl', 'daemon-reload'], check=True)
        print("Systemd daemon reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reload systemd daemon: {e}")


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