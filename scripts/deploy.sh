#!/usr/bin/env bash
sudo apt-get install python3 virtualenv -y

sudo systemctl stop civbot.service

virtualenv ./venv -p python3
source ./venv/bin/activate
pip install -r requirements.txt

sudo cp ./scripts/civbot.service /etc/systemd/system/civbot.service -f

sudo systemctl daemon-reload
sudo systemctl start civbot.service
sudo systemctl enable civbot.service