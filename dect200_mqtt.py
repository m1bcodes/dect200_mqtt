import argparse
import configparser
import traceback
import time
import datetime
import paho.mqtt.client as mqtt
from PyDect200 import PyDect200

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
   
def convertStringToTopic(s : str) -> str:
    return "Device1"

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
        if args.verbose:
            print(devIds)

        for devId in devIds:
            devName =  dect.get_device_name(devId)
            energy = dect.get_energy_single(devId)
            power = dect.get_power_single(devId)
            temperature = dect.get_temperature_single(devId)
            status = dect.get_state(devId)

            if True or args.verbose:
                print(datetime.datetime.now(), ": Device id: ", devId)
                print("Device name: " ,devName)
                print("Energy: ", energy)
                print("Power: ", power)
                print("Temperature: ", temperature)
                print("Status: ", status)
                print("")

            topic = "dect200/" + convertStringToTopic(devName) + "/"
            mqttc.publish(topic + "energy", energy)
            mqttc.publish(topic + "power", power)
            mqttc.publish(topic + "temperature", temperature)
            mqttc.publish(topic + "status", status)

        time.sleep(args.interval)

