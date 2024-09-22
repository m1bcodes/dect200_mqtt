# dect200_mqtt
Queries the status of AVM's Dect200 smart plugs and sends the statistics to an MQTT broker
It builds upon the [PyDect200](https://github.com/mperlet/PyDect200) package.
## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/m1bcodes/dect200_mqtt.git
   ```
2. Navigate to the project directory and install dependencies:
   ```
   cd dect200_mqtt
   pip install -r requirements.txt
   ```

## Usage
Start dect200_mqtt with the required options:
```
python dect200_mqtt.py --help
usage: dect200_mqtt [-h] --fritzuser FRITZUSER --fritzpw FRITZPW --mqttbroker MQTTBROKER [--interval INTERVAL] [-t TOPIC] [-v]

queries the status of AVM's DECT200 smart plugs and publishes the status to a mqtt broker.

options:
  -h, --help            show this help message and exit
  --fritzuser FRITZUSER
  --fritzpw FRITZPW
  --mqttbroker MQTTBROKER
                        Name or address of the mqtt broker. Default port will be used.
  --interval INTERVAL   interval between polls and updates sent. Default: 30 seconds, which is the update rate for power measurement.
  -t TOPIC, --topic TOPIC
                        mqtt topic. (default 'dect200')
  -v, --verbose         provides more output and diagnostic messages.

Example: dect200_mqtt --fritzuser=fritzXXXX --fritzpw=1234 --mqttbroker=servername
```
It will loop forever and emit a json string containing the data acquired from the DECT200 devices connected to the Fritz!Box:

```
{
   "devId": "xxxxxx",               // device id (as printed on the device)
   "devName": "FRITZ!DECT 200",     // the device name, can be configured via
                                       Fritz Box configuration screen.
   "energy": "15",                  // total energy consumed in mWh
   "power": "0",                    // current power in mW
   "temperature": 24.5,             // current temperature in °C
   "status": "1"                    // status of plug outlet. (1: On, 0: Off)
}
```



