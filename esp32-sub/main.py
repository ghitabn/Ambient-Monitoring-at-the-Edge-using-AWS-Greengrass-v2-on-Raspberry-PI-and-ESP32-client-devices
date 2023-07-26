print('Main.py -> Start')
import sys
import config
import os
import time
import random
import ujson
import esp32
import machine
from umqtt.simple import MQTTClient

from machine import Pin

print('Main.py -> Init')
info = os.uname()
with open("/flash/" + config.THING_PRIVATE_KEY, 'r') as f:
    key = f.read()
with open("/flash/" + config.THING_CLIENT_CERT, 'r') as f:
    cert = f.read()
client_id = config.THING_ID
topic_sub = "clients/MyClientDeviceESP-01/sensor01"
aws_endpoint = config.MQTT_HOST
ssl_params = {"key":key, "cert":cert, "server_side":False}

sub_led = Pin(19, Pin.OUT)
sub_led.value(0)

def mqtt_connect(client=client_id, endpoint=aws_endpoint, sslp=ssl_params):
    print("CONNECTING TO MQTT BROKER...")
    mqtt = MQTTClient(
        client_id=client,
        server=endpoint,
        port=8883,
        keepalive=4000,
        ssl=True,
        ssl_params=sslp)
    try:
        mqtt.connect()
        print("MQTT BROKER CONNECTION SUCCESSFUL: ", endpoint)
    except Exception as e:
        print("MQTT CONNECTION FAILED: {}".format(e))
        machine.reset()
    return mqtt

def mqtt_subscribe(topic, message):
    message = ujson.loads(message)
    sub_led.value(1)
    time.sleep(.1)
    sub_led.value(0)
    print("RECEIVING MESSAGE: {} FROM TOPIC: {}".format(message, topic))

print('Main.py -> Setup')
mqtt = mqtt_connect()
mqtt.set_callback(mqtt_subscribe)
mqtt.subscribe(topic_sub)

print('Main.py -> Loop')
while True:
    try:
        mqtt.check_msg()
    except OSError as e:
        print("RECONNECT TO MQTT BROKER")
        mqtt = mqtt_connect()
        mqtt.set_callback(mqtt_subscribe)
        mqtt.subscribe(topic_sub)
    except Exception as e:
        print("A GENERAL ERROR HAS OCCURRED: {}".format(e))
        machine.reset()
