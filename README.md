# Ambient-Monitoring-at-the-Edge
Ambiental telemetry (temperature and humidity) at the edge using AWS Greengrass v2 on Raspberry PI and ESP32 client devices (MicroPython).

AWS Greengrass v2 is installed on a Raspberry Pi (core device); components deployed (to secure connections between clients and the core device and communication with AWS IoT Core):
- Client device auth (aws.greengrass.clientdevices.Auth) - enables client devices to connect to the core device.
- MQTT 3.1.1 broker (Moquette) (aws.greengrass.clientdevices.mqtt.Moquette) - MQTT 3.1.1 broker that handles messages between client devices and the core device
- MQTT bridge (aws.greengrass.clientdevices.mqtt.Bridge) - relays MQTT messages between client devices, local AWS IoT Greengrass publish/subscribe, and AWS IoT Core
- IP detector (aws.greengrass.clientdevices.IPDetector) - reports MQTT broker connectivity information, so client devices can discover how to connect

2 x ESP32 development boards using MicroPython as client devices:
Publisher: reads data (temperature and humidity) from the attached sensor (DHT11)and publish it to an MQTT topic (serial connection, witness LEDs for Tx/Rx)
Subscriber: subscribes to the MQTT topic and receives published telemetry data (serial connection, witness LED Rx)
![image](https://github.com/ghitabn/Ambient-Monitoring-at-the-Edge/assets/127143941/9f1e400f-ea41-4024-a639-97d2e0310cf3)

Hardware:
- 1x Raspberry Pi 4B 4GB (core device) ()
- 2x DOIT ESP32 DEVKIT V1 (client devices) ()
- 1x DHT11 (temperature and humidity sensor)
- 3x LED (signaling)
- 3x 220 ohm (pull-up resistors for LEDs)
- breadboard and wires

Steps:
  1. Set up AWS IoT Greengrass V2 on Raspberry Pi: https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started.html, steps 1-3
     - Install Raspberry Pi OS: https://www.raspberrypi.com/software/
     - Install Greengrass V2
     
