import json
import time
import paho.mqtt.client as mqtt
from termcolor import colored
debug = False
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        if debug:
            print("Connected to broker")
        global Connected  # Use global variable
        Connected = True  # Signal connection
        client.subscribe(data["DEVICE_DATA"]["DEVICE_FOOTPRINT"])
    else:
        if debug:
            print("Connection failed")

def on_message(client, userdata, msg):
    in_data = json.loads((msg.payload).decode("utf-8"))
    if in_data["DEVICE_AUTH"]["DEVICE_USR"]== data["DEVICE_AUTH"]["DEVICE_USR"] and in_data["DEVICE_AUTH"]["DEVICE_PWD"]== data["DEVICE_AUTH"]["DEVICE_PWD"]:
        print("AUTH DONE")
        time.sleep(1)
        MQTT_client.publish(topic=data["DEVICE_DATA"]["ORG_ID"], payload="AUTHENTICATION SUCCESFULLY DONE ON DEVICE END....",
                            qos=int(data["MQTT_PARAM"]["MQTT_QOS"]))
        if in_data["DEVICE_DATA"]["DEVICE_ID"] == data["DEVICE_DATA"]["DEVICE_ID"]:
            print("THIS DATA IS FOR ME")
            MQTT_client.publish(topic=data["DEVICE_DATA"]["ORG_ID"],
                                payload="CONNECTION ACCEPTED BY DEVICE BY RECOGNIZE FOOTPRINT/DEVICEID",
                                qos=int(data["MQTT_PARAM"]["MQTT_QOS"]))
            with open('../MAIN_PROG/cloud_config.json') as json_file:
                data_r = json.load(json_file)
                temp = data_r
                temp["MQTT_PARAM"]["MQTT_URL"] = in_data["MQTT_PARAM"]["MQTT_URL"]
                temp["MQTT_PARAM"]["MQTT_PORT"] = in_data["MQTT_PARAM"]["MQTT_PORT"]
                temp["MQTT_PARAM"]["MQTT_USR"] = in_data["MQTT_PARAM"]["MQTT_USR"]
                temp["MQTT_PARAM"]["MQTT_PASS"] = in_data["MQTT_PARAM"]["MQTT_PASS"]
                temp["MQTT_PARAM"]["MQTT_QOS"] = in_data["MQTT_PARAM"]["MQTT_QOS"]
                temp["MQTT_PARAM"]["MQTT_PUB_TOPIC"] = in_data["MQTT_PARAM"]["MQTT_PUB_TOPIC"]
                temp["MQTT_PARAM"]["MQTT_SUB_TOPIC"] = in_data["MQTT_PARAM"]["MQTT_SUB_TOPIC"]
                temp["MQTT_PARAM"]["CONFIGURE_TIMES"] = temp["MQTT_PARAM"]["CONFIGURE_TIMES"] + 1
            with open('../MAIN_PROG/cloud_config.json', 'w') as file:
                json.dump(temp,file,indent = 4, sort_keys=True)
                print(file)
                print("Cloud configuration done")
                MQTT_client.publish(topic=data["DEVICE_DATA"]["ORG_ID"],
                                    payload="CLOUD CONFIGURATION SUCCESSFULLY LOADED, IT WILL APPLY ONCE DEVICE REBOOT NEXT TIME...",
                                    qos=int(data["MQTT_PARAM"]["MQTT_QOS"]))


        else:
            print("THIS DATA IS NOT FOR ME")
            MQTT_client.publish(topic=data["DEVICE_DATA"]["ORG_ID"],
                                payload="CONNECTION REJECTED BY DEVICE NOT FOR MY USE",
                                qos=int(data["MQTT_PARAM"]["MQTT_QOS"]))
    else:
        print("AUTH FAILLED")
        MQTT_client.publish(topic=data["DEVICE_DATA"]["ORG_ID"],
                            payload="CONNECTION REFUSED DUE TO WRONG AUTHENTICTION",
                            qos=int(data["MQTT_PARAM"]["MQTT_QOS"]))

Connected = False  # global variable for the state of the connection
with open('device_config.json') as json_file:
    data = json.load(json_file)
    if debug:
        print(colored("SUCCESFULLY LOADED CONFIGURATION FROM FILE", "green"))
MQTT_client = mqtt.Client(data["DEVICE_DATA"]["DEVICE_ID"])
MQTT_client.username_pw_set(data["MQTT_PARAM"]["MQTT_USR"], data["MQTT_PARAM"]["MQTT_PASS"])
MQTT_client.on_connect = on_connect  # attach function to callback
MQTT_client.on_message = on_message  # attach function to callback
MQTT_client.connect(data["MQTT_PARAM"]["MQTT_URL"], int(data["MQTT_PARAM"]["MQTT_PORT"]))
print("CONNECTED")
if debug:
    print(colored("SUCCESFULLY CONNECTED TO MQTT BROKER", "green"))
MQTT_client.loop_start()
while Connected != True:  # Wait for connection
    time.sleep(0.1)
try:
    while True:
        payload = data["DEVICE_DATA"]
        MQTT_client.publish(topic=data["DEVICE_DATA"]["ORG_ID"], payload=json.dumps(payload), qos=int(data["MQTT_PARAM"]["MQTT_QOS"]))
        print("PINGING...")
        if debug:
            print(colored("PUBLISHING  DATA TO MQTT-:" + str(payload), "green"))
        time.sleep(5)
except KeyboardInterrupt:
    if debug:
        print("exiting")
    MQTT_client.disconnect()
    MQTT_client.loop_stop()


