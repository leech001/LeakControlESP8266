#import sys
#import os
#import esp
import wifi
import time
import gc
from umqtt.robust import MQTTClient
from machine import Pin
#from machine import Timer
from wsensor import WS
from tap import Tap

#esp.osdebug(0)
gc.enable()

wifi.activate()

TOPIC_PREFIX = b"bath/small/"

tap_cold = Tap(2)
tap_hot = Tap(1)

def check_sensor():
    ws = (WS(16), WS(17))   # Water sensor tuples (pin)
    for item in ws:
        if item.check() == 1:
            client.publish(TOPIC_PREFIX + b"water", "yes")
            tap_cold.close()
            tap_hot.close()


def sub_cb(topic, msg):
    print(topic, msg)
    if topic == (TOPIC_PREFIX + b"/tap/"):
        if msg == b"/close":
            tap_cold.close()
        if msg == b"open":
            tap_cold.open()


client = MQTTClient("ESPython", "192.168.0.21", port=1883, user="user", password="private")
client.DEBUG = True
client.set_callback(sub_cb)
client.connect()
client.subscribe(TOPIC_PREFIX + b"#")


# tim = Timer(-1)
# tim.init(period=10000, mode=Timer.PERIODIC, callback=lambda t:reconnect())


while True:
    client.check_msg()
    time.sleep(1)
#
