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

### Hardware:
- 1x Raspberry Pi 4B 4GB (core device) ()
- 2x DOIT ESP32 DEVKIT V1 (client devices) ()
- 1x DHT11 (temperature and humidity sensor)
- 3x LED (signaling)
- 3x 220 ohm (pull-up resistors for LEDs)
- breadboard and wires

### Install Raspberry Pi OS
1. Download and install the Raspberry Pi Imager for your OS from the official website (https://www.raspberrypi.com/software/);
2. Insert the SD card into your laptop (use an adapter if needed) and launch the software;
3. Select the Operating System to install: Raspberry Pi OS (use a 64-bit version for newest ARM chips);
4. Select the SD Card as target storage;
5. Advanced options:
  - Leave the hostname with default value;
  - Enable SSH and set password;
  - Configure the WiFi;
  - Change Wireless LAN country according to your location;
  - Save;
6. Press Write and wait until the end of the write operation;
7. Safely eject the flashed SD card from the laptop;
8. Insert the SD card into the Raspberry Pi and power it up;
9. Test SSH connection from your laptop to the Raspberry Pi (use Putty or other SSH client).

### Install the AWS IoT Greengrass Core software on Raspberry Pi
1. Set up an AWS account: https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-set-up-aws-account.html
2. Set up the environment: https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-set-up-environment.html, section "Set up a Linux device (Raspberry Pi)" only
3. Create an IAM policy:
   - name: GreengrassV2DeviceProvisionPolicy
   - permissions: copy-paste the content of GreengrassV2DeviceProvisionPolicy.json and replace account-id (rows 16 and 17) with your own account id
4. Create an IAM user to be used by the installer and save the access keys
   - name: RPIGG2User
   - policy: GreengrassV2DeviceProvisionPolicy
6. Install the AWS IoT Greengrass Core software (console): https://docs.aws.amazon.com/greengrass/v2/developerguide/install-greengrass-v2-console.html with the following configuration:
   - use the access keys saved in the previous step for the user RPIGG2User
   - core device name: MyGreengrassRPI
   - thing group name: MyGreengrassGroup
   
### Deploy Greengrass V2 components for local devices
1. From the AWS Management Console navigate to AWS IoT --> Greengrass Devices --> Core devices and select MyGreengrassRPI
2. Select Client devices tab and click Configure cloud discovery
3. Leave the step 1 and step 2 as they are, continue with the step 3
