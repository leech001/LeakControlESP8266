# import sys
# import os
import gc
import time

import esp
from tap import Tap
from umqtt.robust import MQTTClient
# from machine import Timer
from wsensor import WS

from src.esp8266 import wifi

esp.osdebug(0)
gc.enable()

wifi.activate()

TOPIC_PREFIX = b"bath/small/"

tap_cold = Tap(5 , 0)   #D1
tap_hot = Tap(4 , 2)    #D2
ws = (WS(14), WS(12))   # Water sensor tuples (pin)


def check_sensor():
    for item in ws:
        if item.check() == 0:
            print("Water on floor!")
            client.publish(TOPIC_PREFIX + b"water/", "yes")
            tap_cold.close()
            tap_hot.close()
            time.sleep(60)


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


client = MQTTClient("ESPython_small", "192.168.0.70", port=1883, user="user", password="pass")
client.DEBUG = True
client.set_callback(sub_cb)
client.connect()
client.subscribe(TOPIC_PREFIX + b"#")


while True:
    check_sensor()
    client.check_msg()
    time.sleep(1)
