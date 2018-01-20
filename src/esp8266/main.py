import esp
import gc
import wifi
import machine
import utime as time
import usocket as socket
import ustruct as struct
from umqtt.robust import MQTTClient
from machine import Timer
import config

esp.osdebug(0)
gc.enable()
wifi.activate()
tim = Timer(-1)


def time_now():
    ntp_query = bytearray(48)
    ntp_query[0] = 0x1b
    addr = socket.getaddrinfo(config.host, 123)[0][-1]
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(1)
    s.sendto(ntp_query, addr)
    msg = s.recv(48)
    s.close()
    val = struct.unpack("!I", msg[40:44])[0]
    return val - config.ntp_delta


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
    for item in config.ws:
        if item.check() == 0:
            print("Water on floor!")
            client.publish(config.CONFIG['TOPIC'] + b"water/", "yes")
            config.tap_cold.close()
            config.tap_hot.close()
        print("Check sensor %d", item.check())


def sub_cb(topic, msg):
    print("Topic: %s, Message: %s" % (topic, msg))
    s_topic = str(topic).split("/")

    if s_topic[2] == "tap":
        if s_topic[3] == "cold":
            if msg == b"close":
                print(config.tap_cold.close())
            if msg == b"open":
                print(config.tap_cold.open())
        elif s_topic[3] == "hot":
            if msg == b"close":
                print(config.tap_hot.close())
            if msg == b"open":
                print(config.tap_hot.open())


def mqtt_reconnect():
    # Create an instance of MQTTClient
    global client
    client = MQTTClient(config.CONFIG['CLIENT_ID'], config.CONFIG['MQTT_BROKER'], user=config.CONFIG['USER'], password=config.CONFIG['PASSWORD'],
                        port=config.CONFIG['PORT'])
    # Attach call back handler to be called on receiving messages
    client.DEBUG = True
    client.set_callback(sub_cb)
    client.connect(clean_session=True)
    client.subscribe(config.CONFIG['TOPIC'] + b"#")
    print("ESP8266 is Connected to %s and subscribed to %s topic" % (config.CONFIG['MQTT_BROKER'], config.CONFIG['TOPIC']))


tim.init(period=5000, mode=Timer.PERIODIC, callback=lambda t: check_sensor())

i = 2
try:
    while True:
        ping_test = internet_connected()
        if ping_test and i == 0:
            # Check topic
            client.check_msg()
        elif ping_test and i == 1:
            # New session
            mqtt_reconnect()
            client.check_msg()
            i = 0
        elif ping_test is False and i == 0:
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
        time.sleep(1)
        continue
except OSError as e:
    print(e)
    time.sleep(60)
    machine.reset()

client.disconnect()