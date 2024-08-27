# Car Detector Service

This repository contains the main Python script and associated files for the Car Detector service. The service is managed by systemd and is designed to run on a Linux operating system.

## Prerequisites

- Python 3.x
- Virtualenv
- Systemd

## Setup

1. **Clone the repository:**

    ```sh
    git clone https://github.com/rashidiy/CarDetector-MachineSide.git
    cd CarDetector-MachineSide
    ```

2. **Create a virtual environment and activate it:**

    ```sh
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the required Python packages:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Create a `.env` file in the root directory of the project:**

    ```sh
    touch .env
    ```

5. **Add the necessary environment variables to the `.env` file:**

    ```ini
    COMPANY_ID=<your_company_id>
    SECURITY_KEY=<company_security_key>
    HOST=skud.ekom.uz
    PORT=6080
    PY_PATH=/root/CarDetector-MachineSide/venv/bin/python3
    ```

## Systemd Service Setup

1. **Create a systemd service file:**

    ```sh
    sudo nano /etc/systemd/system/cardetector.service
    ```

2. **Add the following content to the service file:**

    ```ini
    [Unit]
    Description=Main Python Script Service for Car Detector
    After=network.target

    [Service]
    User=root
    Group=root
    WorkingDirectory=/root/CarDetector-MachineSide/
    ExecStart=/root/CarDetector-MachineSide/venv/bin/python3 /root/CarDetector-MachineSide/main.py
    EnvironmentFile=/root/CarDetector-MachineSide/.env
    Restart=always
    RestartSec=10

    [Install]
    WantedBy=multi-user.target
    ```

3. **Reload systemd to recognize the new service:**

    ```sh
    sudo systemctl daemon-reload
    ```

4. **Enable and start the service:**

    ```sh
    sudo systemctl enable cardetector
    sudo systemctl start cardetector
    ```

5. **Check the status of the service:**

    ```sh
    sudo systemctl status cardetector
    ```

## Usage

The Car Detector service will start automatically on boot and will restart if it crashes. You can manage the service using standard systemd commands:

- Start the service:

    ```sh
    sudo systemctl start cardetector
    ```

- Stop the service:

    ```sh
    sudo systemctl stop cardetector
    ```

- Restart the service:

    ```sh
    sudo systemctl restart cardetector
    ```

- Check the status of the service:

    ```sh
    sudo systemctl status cardetector
    ```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Acknowledgements

- Thanks to all the contributors who have made this project possible.
