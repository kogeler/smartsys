#!/bin/bash


sudo apt-get install python3-venv
python3 -m venv venv
source venv/bin/activate
pip3 install jsonschema
pip3 install paho-mqtt
pip3 install psycopg2
pip3 install python-telegram-bot
pip3 install PyYAML
pip3 install RPi.bme280
pip3 install RPi.GPIO
pip3 list
deactivate


