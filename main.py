# import sys
# import os
import esp
import wifi
import time
import gc
from umqtt.robust import MQTTClient
# from machine import Pin
# from machine import Timer
from wsensor import WS
from tap import Tap

esp.osdebug(0)
gc.enable()

wifi.activate()

TOPIC_PREFIX = b"bath/small/"

tap_cold = Tap(2)
tap_hot = Tap(1)
ws = (WS(16), WS(5), WS(4), WS(0), WS(2))   # Water sensor tuples (pin)


def check_sensor():
    for item in ws:
        if item.check() == 0:
            print("Water on floor!")
            client.publish(TOPIC_PREFIX + b"water/", "yes")
            tap_cold.close()
            tap_hot.close()


def sub_cb(topic, msg):
    print(topic, msg)
    s_topic = str(topic).split("/")

    if s_topic[2] == "tap":
        if s_topic[3] == "cold":
            if msg == b"close":
                print(tap_cold.close())
            if msg == b"open":
                print(tap_cold.open())
        elif s_topic[3] == "hot":
            if msg == b"close":
                print(tap_hot.close())
            if msg == b"open":
                print(tap_hot.open())


client = MQTTClient("ESPython", "192.168.0.21", port=1883, user="user", password="private")
# client = MQTTClient("ESPython", "broker.mqttdashboard.com", port=8000)
client.DEBUG = True
client.set_callback(sub_cb)
client.connect()
client.subscribe(TOPIC_PREFIX + b"#")


# tim = Timer(-1)
# tim.init(period=10000, mode=Timer.PERIODIC, callback=lambda t:reconnect())


while True:
    check_sensor()
    client.check_msg()
    time.sleep(1)


