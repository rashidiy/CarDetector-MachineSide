import os

from dotenv import load_dotenv

load_dotenv()

CAMERA_ID = os.getenv('CAMERA_ID')
SECURITY_KEY = os.getenv('SECURITY_KEY')

SERVER_URL = os.getenv('SERVER_URL')
DAHUA_CAMERA_URL = os.getenv('DAHUA_CAMERA_URL')
DAHUA_CAMERA_LOGIN = os.getenv('DAHUA_CAMERA_LOGIN')
DAHUA_CAMERA_PASSWORD = os.getenv('DAHUA_CAMERA_PASSWORD')

WIFI_SSID = os.getenv('WIFI_SSID')
WIFI_PASSWORD = os.getenv('WIFI_PASSWORD')
