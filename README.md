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
    - Client device auth - aws.greengrass.clientdevices.Auth: config/aws.greengrass.clientdevices.Auth.json
    - MQTT 3.1.1 broker (Moquette) - aws.greengrass.clientdevices.mqtt.Moquette: config/aws.greengrass.clientdevices.mqtt.Moquette.json
    - MQTT bridge - aws.greengrass.clientdevices.mqtt.Bridge: config/aws.greengrass.clientdevices.mqtt.Bridge.json
    - IP detector - aws.greengrass.clientdevices.IPDetector): -
   
   execute the following update sequence:
   - select the component
   - choose Edit configuration
   - paste the configuration to merge (from the corresponding .json file)
   - press Confirm

5. Click Review and deploy and choose Grant permissions
6. Click Deploy
