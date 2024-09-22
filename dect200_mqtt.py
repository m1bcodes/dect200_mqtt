import argparse
import configparser
import traceback
import time
import datetime
import paho.mqtt.client as mqtt
from PyDect200 import PyDect200
import json

def check_positive(value):
    ivalue = int(value)
    if ivalue < 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue

def parseCommandLine():
    parser = argparse.ArgumentParser(
        prog = "dect200_mqtt",
        description = "queries the status of AVM's DECT200 smart plugs and publishes the status to a mqtt broker.",
        epilog = "Example: dect200_mqtt --fritzuser=fritzXXXX --fritzpw=1234 --mqttbroker=servername")

    parser.add_argument("--fritzuser", required=True)
    parser.add_argument("--fritzpw", required=True)
    parser.add_argument("--mqttbroker", required=True, help="Name or address of the mqtt broker. Default port will be used.")
    parser.add_argument("--interval", required=False, default=30, type=check_positive, help="interval between polls and updates sent. Default: 30 seconds, which is the update rate for power measurement.")
    parser.add_argument("-t", "--topic", required=False, default="dect200", help="mqtt topic. (default 'dect200')")
    parser.add_argument("-v", "--verbose", action='store_true', default=False, help="provides more output and diagnostic messages.")
    args = parser.parse_args()
    return args        

# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("$SYS/#")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))
   
def readDect(dect : PyDect200.PyDect200, devId : str) -> dict:
    m = dict()
    m["devId"] = devId
    m["devName"] =  dect.get_device_name(devId)
    m["energy"] = dect.get_energy_single(devId)
    m["power"] = dect.get_power_single(devId)
    m["temperature"] = dect.get_temperature_single(devId)
    m["status"] = dect.get_state(devId)
    return m

def convertStringToTopic(s : str) -> str:
    outStr = ""
    for ch in s:
        if ch.isalnum():
            outStr += ch
        elif len(outStr)==0 or outStr[-1]!='_':
            outStr += '_'
    return outStr

if __name__ == "__main__":      
    args = parseCommandLine()

    dect = PyDect200.PyDect200(args.fritzpw, username=args.fritzuser)
    if not dect.login_ok():
        raise Exception("Login to friz-box not successful.")        

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    if args.verbose:
        mqttc.on_connect = on_connect
        mqttc.on_message = on_message

    if args.verbose:
        mqttc.enable_logger()        
    mqttc.connect(args.mqttbroker, 1883, 60)
    mqttc.loop_start()

    while True:
        devIds = dect.get_device_ids()
        for devId in devIds:
            m = readDect(dect, devId)
            
            jsonString = json.dumps(m)
            topic = args.topic + "/" + convertStringToTopic(m["devName"])
            if args.verbose:
                print("%s: %s: %s" % (datetime.datetime.now(), topic, jsonString))
            mqttc.publish(topic, jsonString)

        time.sleep(args.interval)

