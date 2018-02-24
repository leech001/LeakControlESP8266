import gc
import wifi
import machine
import utime as time
import usocket as socket
import ustruct as struct
from umqtt.robust import MQTTClient
from machine import Timer
import config

gc.enable()
wifi.activate()
tim_1 = Timer(-1)
tim_2 = Timer(-1)
int_err_count = 0
ping_mqtt = 0
ping_fail = 0


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
    print("Check sensor ...")
    for item in config.ws:
        if item.check() == 0:
            print("Water on floor!")
            client.publish(config.CONFIG['TOPIC'] + b"water/", "yes")
            close_tap()


def close_tap():
    config.tap_cold.close()
    config.tap_hot.close()


def on_message(topic, msg):
    global ping_fail
    print("Topic: %s, Message: %s" % (topic, msg))
    s_topic = str(topic).split("/")

    if s_topic[2] == "ping":
        if int(msg) == ping_mqtt:
            print("MQTT pong true...")
            ping_fail = 0
        else:
            print("MQTT pong false... (%i)" % ping_fail)
    elif s_topic[2] == "tap":
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
    elif s_topic[2] == "water":
        if msg == b"yes":
            close_tap()


def send_mqtt_ping():
    global ping_fail
    global ping_mqtt
    ping_mqtt = time.time()
    client.publish(config.CONFIG['TOPIC'] + b"ping/", "%s" % ping_mqtt)
    print("Send MQTT ping (%i)" % ping_mqtt)
    ping_fail += 1
    if ping_fail >= config.CONFIG['MAX_MQTT_ERR']:
        print("MQTT ping false... reconnect (%i)" % ping_fail)
        client.disconnect()
        mqtt_reconnect()
        machine.reset()
    elif ping_fail >= config.CONFIG['CRIT_MQTT_ERR']:
        print("MQTT ping false... reset (%i)" % ping_fail)
        machine.reset()


def mqtt_reconnect():
    global client
    global ping_fail
    client = MQTTClient(config.CONFIG['CLIENT_ID'], config.CONFIG['MQTT_BROKER'], user=config.CONFIG['USER'],
                            password=config.CONFIG['PASSWORD'], port=config.CONFIG['PORT'])
    client.DEBUG = True
    client.set_callback(on_message)
    try:
        client.connect(clean_session=True)
        client.subscribe(config.CONFIG['TOPIC']+b"#")
        print("ESP8266 is Connected to %s and subscribed to %s topic" % (config.CONFIG['MQTT_BROKER'], config.CONFIG['TOPIC']+b"#"))
    except OSError:
        machine.reset()


mqtt_reconnect()
tim_1.init(period=5000, mode=Timer.PERIODIC, callback=lambda t: check_sensor())
tim_2.init(period=10000, mode=Timer.PERIODIC, callback=lambda t: send_mqtt_ping())


try:
    while True:
        print("Check message...")
        client.check_msg()
        if not internet_connected():
            print("Internet connect fail...")
            int_err_count += 1
            if int_err_count >= config.CONFIG['MAX_INT_ERR']:
                print("Internet reconnect")
                client.disconnect()
                wifi.wlan.disconnect()
                wifi.activate()
            elif int_err_count >= config.CONFIG['CRIT_INT_ERR']:
                client.disconnect()
                wifi.wlan.disconnect()
                machine.reset()
        time.sleep(1)
        continue
except OSError as e:
    print(e)
    machine.reset()
