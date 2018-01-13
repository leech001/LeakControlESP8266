import gc
import time
import wifi
import machine
import utime as time
import usocket as socket
import ustruct as struct
from umqtt.robust import MQTTClient
from tap import Tap
from wsensor import WS

NTP_DELTA = 3155673600
host = "pool.ntp.org"
tap_cold = Tap(5, 0)  # D1
tap_hot = Tap(4, 2)  # D2
ws = (WS(14), WS(12))  # Water sensor tuples (pin)

gc.enable()
wifi.activate()

# Modify below section as required
CONFIG = {
    # Configuration details of the MQTT broker
    "MQTT_BROKER": "192.168.0.100",
    "USER": "user",
    "PASSWORD": "pass",
    "PORT": 1883,
    "TOPIC": b"bath/small/",
    # unique identifier of the chip
    "CLIENT_ID": b"ESPython_small"
}


def time_now():
    ntp_query = bytearray(48)
    ntp_query[0] = 0x1b
    addr = socket.getaddrinfo(host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    s.sendto(ntp_query, addr)
    msg = s.recv(48)
    s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - NTP_DELTA


# There's currently no timezone support in MicroPython, so
# utime.localtime() will return UTC time (as if it was .gmtime())
def settime():
    t = time_now()
    tm = time.localtime(t)
    tm = tm[0:3] + (0,) + tm[3:6] + (0,)
    machine.RTC().datetime(tm)


settime()


# Check Internet connection
def internet_connected(host='8.8.8.8', port=53):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(1.0)
    try:
        s.connect((host, port))
        return True
    except:
        return False
    finally:
        s.close()


def check_sensor():
    for item in ws:
        if item.check() == 0:
            print("Water on floor!")
            client.publish(CONFIG['TOPIC'] + b"water/", "yes")
            tap_cold.close()
            tap_hot.close()
            time.sleep(60)


def sub_cb(topic, msg):
    print("Topic: %s, Message: %s" % (topic, msg))
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


def mqtt_reconnect():
    # Create an instance of MQTTClient
    global client
    client = MQTTClient(CONFIG['CLIENT_ID'], CONFIG['MQTT_BROKER'], user=CONFIG['USER'], password=CONFIG['PASSWORD'],
                        port=CONFIG['PORT'])
    # Attach call back handler to be called on receiving messages
    client.DEBUG = True
    client.set_callback(sub_cb)
    client.connect(clean_session=True)
    client.subscribe(CONFIG['TOPIC'] + b"#")
    print("ESP8266 is Connected to %s and subscribed to %s topic" % (CONFIG['MQTT_BROKER'], CONFIG['TOPIC']))


i = 2

try:
    while True:
        check_sensor()
        ping_test = internet_connected()
        if ping_test and i == 0:
            # Check topic
            client.check_msg()
        elif ping_test and i == 1:
            # New session
            mqtt_reconnect()
            client.check_msg()
            i = 0
        elif ping_test == False and i == 0:
            # Disconnect
            i = 1
            client.disconnect()
        elif ping_test and i == 2:
            # First connection
            mqtt_reconnect()
            i = 0
        else:
            # No Internet Connection
            pass
        time.sleep(0.5)
        continue
except OSError as e:
    print(e)
    time.sleep(60)
    machine.reset()

client.disconnect()
