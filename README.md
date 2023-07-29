# Ambient-Monitoring-at-the-Edge
Ambiental telemetry (temperature and humidity) at the edge using AWS Greengrass v2 on Raspberry PI and ESP32 client devices (MicroPython).

The project uses a Raspberry Pi running AWS Greengrass v2 as a core device which extends AWS IoT Core functionnality at the edge. It allows MQTT communication between two client devices (ESP32): a publisher and a subscriber. Telemetry data collected by the publisher from a local sensor is available through an MQTT topic to:
- local subscriber(s) for signaling and/or local control (i.e. interfacing and controlling a local HVAC system);
- AWS IoT Core (subject to uplink connectivity) for further processing and visualization.

## Hardware:
- 1x Raspberry Pi 4B 4GB (core device) ()
- 2x DOIT ESP32 DEVKIT V1 (client devices) ()
- 1x DHT11 (temperature and humidity sensor)
- 3x LED (signaling)
- 3x 220 ohm (pull-up resistors for LEDs)
- breadboard and wires

## Setup the hardware
Use the following schematics to setup the hardware:
- core device: provide power through the onboard USB-C port, no additional components
- client devices
    - provide power and serial connectivity through the onboard micro-USB port
    - pub schematics: schematics/client_device_pub_schematics.png
    - sub schematics: schematics/client_device_pub_schematics.png
  
## Configure the Core device
### 1. Install Raspberry Pi OS
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

### 2. Install the AWS IoT Greengrass Core software on Raspberry Pi
1. Set up an AWS account: https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-set-up-aws-account.html
2. Set up the environment: https://docs.aws.amazon.com/greengrass/v2/developerguide/getting-started-set-up-environment.html, section "Set up a Linux device (Raspberry Pi)" only
3. Create an IAM policy:
   - name: GreengrassV2DeviceProvisionPolicy
   - permissions: copy-paste the content of GreengrassV2DeviceProvisionPolicy.json and replace account-id (rows 16 and 17) with your own account id
4. Create an IAM user to be used by the installer and save the access keys
   - name: RPIGG2User
   - policy: GreengrassV2DeviceProvisionPolicy
5. Install the AWS IoT Greengrass Core software (console): https://docs.aws.amazon.com/greengrass/v2/developerguide/install-greengrass-v2-console.html with the following configuration:
   - use the access keys saved in the previous step for the user RPIGG2User
   - core device name: MyGreengrassRPI
   - thing group name: MyGreengrassGroup
   
### 3. Deploy Greengrass V2 components for local devices
1. From the AWS Management Console navigate to AWS IoT -> Greengrass Devices -> Core devices and select MyGreengrassRPI
2. Select Client devices tab and click Configure cloud discovery
3. Leave the step 1 and step 2 as they are and continue with the step 3: for each of the following components
   - Client device auth - aws.greengrass.clientdevices.Auth
   - MQTT 3.1.1 broker (Moquette) - aws.greengrass.clientdevices.mqtt.Moquette
   - MQTT bridge - aws.greengrass.clientdevices.mqtt.Bridge
   - IP detector - aws.greengrass.clientdevices.IPDetector)
   
   execute the following update sequence:
   - select the component
   - choose Edit configuration
   - paste the configuration to merge (from the corresponding .json file)
       - Client device auth: config/aws.greengrass.clientdevices.Auth.json
       - MQTT 3.1.1 broker (Moquette): config/aws.greengrass.clientdevices.mqtt.Moquette.json
       - MQTT bridge: config/aws.greengrass.clientdevices.mqtt.Bridge.json
       - IP detector: no configuration to merge
   - press Confirm

5. Click Review and deploy and choose Grant permissions
6. Click Deploy

## Configure the client devices
**Note.** The steps below are for a Windows local machine. Similar steps can be executed for Linux or MAC.
 
### 1. Flash the ESP32 with MicroPython firmware
1. Install _CP210x USB to UART Bridge VCP Drivers_ on the local machine: https://www.silabs.com/developers/usb-to-uart-bridge-vcp-drivers?tab=overview
2. Install Python 3.x: https://www.python.org/downloads/windows/
3. Install _esptool_ and _MicroPython stubs_ (cmd or PowerShell):
    pip install esptool
    pip install -U  micropython-esp32-stubs
4. Download the latest MycroPython firmware from: https://micropython.org/download/esp32/ (i.e. esp32-20220618-v1.19.1.bin)
5. Identify the COM port in use by the ESP32 board, using Device Manager (i.e. COM4)
6. Erase the flash (cmd or PowerShell):
    python -m esptool --chip esp32 --port COM4 erase_flash
7. Install the firmware (cmd or PowerShell):
    python -m esptool --chip esp32 --port COM4 --baud 460800 write_flash -z 0x1000 esp32-20220618-v1.19.1.bin

**Note.** Depending on the ESP32 board, erasing/writing operations (steps 6 and 7 above) might require to manually put the board Firmware Download boot mode by long pressing the BOOT button.
https://docs.espressif.com/projects/esptool/en/latest/esp32/advanced-topics/boot-mode-selection.html

### 2. Configure the development environment on the local machine
Install VS Code and Pymakr to execute code on a EPS32, directly from a Visual Studio app: https://docs.pycom.io/gettingstarted/software/vscode/

### 3. Create AWS IoT things and associate them with the core device
For both publisher and subscriber:

1. Navigate to the AWS IoT console -> All devices -> Things and click Create things
2. Choose Create single thing and click Next
3. Enter Thing name and click Next
- pub Thing name: MyClientDeviceESP32-01
- sub Thing name: MyClientDeviceESP32-02

4. Choose Auto-generate a new certificate and click Next
5. Click Create thing (do not select/create a policy)
6. Download certificates to the right folder and rename them:
- pub:
    - Amazon root: esp32-pub/flash/AmazonRootCA1.pem
    - Device certificate: esp32-pub/flash/MyClientDeviceESP-01-certificate.pem.crt
    - Private key: esp32-pub/flash/MyClientDeviceESP-01-private.pem.key
    - Public key: esp32-pub/flash/MyClientDeviceESP-01-public.pem.key

- sub:
    - Amazon root: esp32-sub/flash/AmazonRootCA1.pem
    - Device certificate: esp32-sub/flash/MyClientDeviceESP-02-certificate.pem.crt
    - Private key: esp32-sub/flash/MyClientDeviceESP-02-private.pem.key
    - Public key: esp32-sub/flash/MyClientDeviceESP-02-public.pem.key
   
7. Click Finish creating thing
8. Navigate to Manage -> Greengrass devices -> Core devices and click MyGreengrassRPI
9. Go to Client devices tab and record MQTT broker endpoint information (endpoint and port) for later use.
10. Click Associate client devices
11. Enter MyClientDeviceESP32-01 and MyClientDeviceESP32-01 for AWS IoT thing name. Click Add and then Associate.
12. Update WiFi, MQTT and certificates in the configuration files (esp32-pub/config.py and esp32-sub/config.py)
