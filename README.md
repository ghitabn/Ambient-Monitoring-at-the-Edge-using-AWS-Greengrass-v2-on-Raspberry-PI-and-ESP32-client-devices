[1. Description](#1)<br>
[2. AWS Architecture diagram](#2)<br>
[3. Hardware](#3)<br>
[4. Steps](#4)<br>
[4.1. Setup hardware](#41)<br>
[4.2. Configure the core device](#42)<br>
[4.2.1. Install Raspberry Pi OS](#421)<br>
[4.2.2. Install the AWS IoT Greengrass Core software](#422)<br>
[4.2.3. Deploy Greengrass V2 components for client devices](#423)<br>
[4.3. Configure client devices (ESP32s)](#43)<br>
[4.3.1. Create AWS IoT things and associate them with the core device](#431)<br>
[4.3.2. Flash the ESP32 with MicroPython firmware](#432)<br>
[4.3.3. Configure the development environment on the local machine and upload the code to client devices](#433)<br>
[4.4. Test MQTT communication between client devices and relay to AWS IoT Core](#44)<br>
[4.5. Configure IoT Analytics](#45)<br>
[4.5.1. Create a channel in IoT Analytics](#451)<br>
[4.5.2. Add timestamp to the streaming data](#452)<br>
[4.5.3. Create a Datastore](#453)<br>
[4.5.4. Create a Pipeline](#454)<br>
[4.5.5. Create a Dataset](#455)<br>
[4.6. Create visuals in QuickSight](#46)<br>
[4.6.1. Setup the dataset](#461)<br>
[4.6.2. Create visuals](#462)<br>
[4.6.3. Refresh QuickSight data](#463)<br>
[4.7. SNS Notifications](#47)<br> 
<a name="1"></a>
# 1. Description
The project uses a Raspberry Pi running AWS Greengrass v2 as a core device which extends AWS IoT Core functionnality at the edge. It allows MQTT communication between two client devices (ESP32 running MicroPython firmware): a publisher and a subscriber. Telemetry data (temperature and humidity) is collected by the publisher from an attached sensor. It is available to the subscriber(s) for signaling and/or local control (i.e. interfacing and controlling a local HVAC system) and relayed to AWS IoT Core for further processing and visualization. SNS notifications can be used for alerting purposes.
<a name="2"></a>
# 2. AWS Architecture diagram
The AWS architecture diagram is available in the following location: diagrams/architecture/architecture_diagram_aws.png
<a name="3"></a>
# 3. Hardware
- 1x Raspberry Pi 4B 4GB (core device) (https://www.amazon.ca/gp/product/B07TC2BK1X/ref=ppx_yo_dt_b_asin_title_o00_s00?ie=UTF8&psc=1)
- 2x DOIT ESP32 DEVKIT V1 (client devices) (https://www.amazon.ca/KeeYees-Development-Bluetooth-Microcontroller-ESP-WROOM-32/dp/B07QCP2451/ref=sr_1_6?crid=FRGCA0U4QLA6&keywords=DOIT%2BESP32%2BDEVKIT%2BV1&qid=1691051640&s=electronics&sprefix=doit%2Besp32%2Bdevkit%2Bv1%2Celectronics%2C78&sr=1-6&th=1)
- 1x DHT11 (temperature and humidity sensor) (https://www.amazon.ca/CANADUINO-Temperature-Humidity-Sensor-DHT11-16bit/dp/B075CNS7PS/ref=sr_1_4?keywords=dht11+sensor&qid=1691051489&s=electronics&sprefix=dht11%2Celectronics%2C108&sr=1-4)
- 3x LED (signaling)
- 3x 220 ohm (pull-up resistors for LEDs)
- breadboard and wires
<a name="4"></a>
# 4. Steps
<a name="41"></a>
## 4.1. Setup hardware
- core device: provide power through the onboard USB-C port, no additional components required
- client devices
    - provide power and serial connectivity through the onboard micro-USB port
    - use the following schematics to interconnect additional hardware:
        - pub schematics: diagrams/schematics/client_device_pub_schematics.png
        - sub schematics: diagrams/schematics/client_device_pub_schematics.png
<a name="42"></a>  
## 4.2. Configure the core device
<a name="421"></a>
### 4.2.1. Install Raspberry Pi OS
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
8. Insert the SD card into the Raspberry Pi and power it up through the onboard USB-C port (no additional hardware components required);
9. Test SSH connection from your laptop to the Raspberry Pi (use Putty or other SSH client).
<a name="422"></a>
### 4.2.2. Install the AWS IoT Greengrass Core software
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
<a name="423"></a>
### 4.2.3. Deploy Greengrass V2 components for client devices
1. From the AWS Management Console navigate to AWS IoT -> Greengrass Devices -> Core devices and select MyGreengrassRPI
2. Select Client devices tab and click Configure cloud discovery
3. Leave the step 1 and step 2 as they are and continue with the step 3: for each of the components below
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
<a name="43"></a>
## 4.3. Configure client devices (ESP32s)
<a name="431"></a>
### 4.3.1. Create AWS IoT things and associate them with the core device
For each client device (publisher and subscriber):
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
<a name="432"></a>
### 4.3.2. Flash the ESP32 with MicroPython firmware
**Note.** The steps below are specific to a Windows local machine. Similar steps can be executed for Linux or MAC.
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
<a name="433"></a>
### 4.3.3. Configure the development environment on the local machine and upload the code to client devices
1. Install VS Code and Pymakr to execute code on a EPS32, directly from a Visual Studio app: https://docs.pycom.io/gettingstarted/software/vscode/
2. Upload the code to client devices:
   - code for the publisher: esp-32-pub
   - code for the subscriber: esp-32-sub
<a name="44"></a>
## 4.4. Test MQTT communication between client devices and relay to AWS IoT Core
1. Power on the core and client devices
2. Use putty to establish connections:
   - ssh to the core device
   - serial to each client device
3. Check local communication in the serial consoles for publisher and subscriber through the configured MQTT topic (clients/MyClientDeviceESP-01/sensor01)
4. Use AWS IoT MQTT test client to test subscription to the configured topic (clients/MyClientDeviceESP-01/sensor01)   
<a name="45"></a>
## 4.5. Configure IoT Analytics
<a name="451"></a>
### 4.5.1. Create a channel in IoT Analytics
   - Navigate to the AWS IoT Analytics console -> Click on Channels -> Click on Create channel -> CreateChannel 
   - Channel name: sensorchannel
   - Select the "Service-managed Store"
   - Set the "Choose how long to store your raw data" option to "Specified time period"
   - Data Retention: 5 days
   - Click on Next
   - IoT Core Topic Filter: clients/MyClientDeviceESP-01/sensor01
   - IAM role name: Create new
   - Rule Name: IoTAnalyticsSensorRole
   - Click on Create Role
   - Click on Next
   - Click on Create Channel
   - Verify the rule IoTAnalytics_sensorchannel has been succesfully created in AWS IoT -> Manage -> Message routing -> Rules in your AWS console
<a name="452"></a>
### 4.5.2. Add timestamp to the streaming data
   - Navigate to AWS IoT -> Manage -> Message routing -> Rules in your AWS console
   - Click on the rule IoTAnalytics_sensorchannel
   - Click edit in the top right hand corner
   - Change the SQL statement from
         SELECT * FROM 'clients/MyClientDeviceESP-01/sensor01'
         to
         SELECT *, parse_time("yyyy-MM-dd'T'HH:mm:ss.SSSZ", timestamp()) as RealTime FROM 'clients/MyClientDeviceESP-01/sensor01'
    - Click Update
<a name="453"></a>
### 4.5.3. Create a Datastore
   - Navigate to IoT Analytics dashboard -> click on Data stores -> Create a data store
   - Data store ID: iotsensordatastore
   - Click on Next
   - Select the "Service-managed Store"
   - Set the "Configure how long you want to keep your processed data" option to "Specified time period"
   - Data Retention: 5 days
   - Click on Next
   - Keep the default and click on Next on the Choose data format screen
   - Keep the default and click on Next on the Add data partitions - optional screen
   - Click on Create data store
<a name="454"></a>
### 4.5.4. Create a Pipeline
   - Navigate to IoT Analytics dashboard -> click on Pipelines -> Create a pipeline
   - Pipeline name: iotsensorpipeline
   - Pipeline source: sensorchannel
   - Pipeline output: iotsensordatastore
   - Click Next
   - Click Next, to get to the Pipeline Activities section.
     **Note.** On this page, we will add a new calculated attribute to the data (temperature in Fahrenheit).
   - Click the drop-down menu and choose Calculate a message attribute and click Add.
   - Under Calculate a message attribute:
       - Attribute name: sensors.temperature_f
       - Formula: sensors.temperature * 9/5 + 32
       - Click Update Preview to see a preview.
   - Click the drop-down menu and choose Select message attributes and click Add.
       - Select sensors.humidity, sensors.temperature and RealTime
   - Click on Next
   - Click Create pipeline
<a name="455"></a>
### 4.5.5. Create a Dataset
   - Navigate to IoT Analytics dashboard -> click on Datasets -> Create a Dataset
   - Select Create SQL
   - Dataset name: iotsensordataset
   - Data store source: iotsensordatastore
   - Click Next
   - SQL Statement: SELECT * FROM iotsensordatastore
   - Click Next
   - Click Next on the "Data Selection Filter"
   - Schedule: Select Every 1 minute
   - "Configure the results of your dataset": leave the defaults and click Next
   - "Configure dataset content delivery rules - optional": leave the defaults and click Next
   - Click Create data set
<a name="46"></a>
## 4.6. Create visuals in QuickSight
<a name="461"></a>
### 4.6.1. Setup the dataset
   - Navigate to the QuickSight dashboard and select the us-east-2 region
   - Click on Datasets
   - Click on New dataset
   - Select IoT Analytics
   - Select the IoT Analytics dataset previously created (iotsensordataset)
   - Click Create data source
   - Click Visualize
   - Ensure Interactive sheet is selected and click Create
<a name="462"></a>
### 4.6.2. Create visuals
   - Crete the following visuals:
   - Average of Temperature by RealTime:
       - X axis: realtime (SECOND)
       - Y axis: temperature (Average)
   - Average of Humidity by RealTime:
       - X axis: realtime (SECOND)
       - Y axisL humidity (Average)
   - Average of Temperature_f by RealTime:
       - X axis: realtime (SECOND)
       - Y axisL temperature (Average)
<a name="463"></a>
### 4.6.3. Refresh QuickSight data
   - Manual refresh:
       - Navigate to the QuickSight console
       - Click on Datasets
       - Click on the dataset iotsensordataset
       - Click on the Refresh tab
       - Click REFRESH NOW to refresh your dataset
   - Automated refresh (based on schedule)
        - Click on Add new schedule
            - Occurence: Daily
            - Start time: 23:59
            - Timezone: America/Toronto
<a name="47"></a>
## 4.7. SNS Notifications
1. Creating a new SNS topic
   - Navigate to Amazon SNS console
   - Click Create topic
       - Type: Standard
       - Name: iotsensorsnstopic
   - Record the ARN for the new topic for next step
2. Create a new IoT rule
   - Navigate to the AWS IoT core dashboard -> Message routing -> Rules
   - Click on Create rule
       - Rule name: sns_notification_sensor
       - SQL Statement:
            SELECT sensors.temperature, sensors.humidity FROM 'clients/MyClientDeviceESP-01/sensor01' WHERE sensors.temperature > 35 OR sensors.humidity > 95
        - Rule actions: Select Simple Notification Service (SNS)
        - SNS topic: select the ARN for the topic created in the previous step
        - Message format: RAW
        - IAM role:
            - Click on Create new role
                - Name: iotsensorsnsrole
                - Permissions: AmazonSNSFullAccess
        - Click on Next
        - Click on Create
3. Create a subscription to the SNS topic and test SNS notifications
