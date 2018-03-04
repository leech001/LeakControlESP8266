import gc
import uasyncio as asyncio
import wifi
import machine
import utime as time
import usocket as socket
import ustruct as struct
from umqtt.simple import MQTTClient
import config

gc.enable()
wifi.activate()
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
    global int_err_count
    while True:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1.0)
        try:
            s.connect((host, port))
            int_err_count = 0
            return True
        except Exception as e:
            print("Error Internet connect: [Exception] %s: %s" % (type(e).__name__, e))
            return False
        finally:
            s.close()


# Check sensor
async def check_sensor():
    while True:
        await asyncio.sleep_ms(1000)
        print("Check sensor ...")
        for item in config.ws:
            if item.check() == 0:
                print("Water on floor!")
                close_tap()
                client.publish(config.CONFIG['TOPIC'] + b"water/", "yes")


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


# Ping MQTT brocker
async def send_mqtt_ping():
    global ping_fail
    global ping_mqtt
    while True:
        await asyncio.sleep_ms(5000)
        ping_mqtt = time.time()
        client.publish(config.CONFIG['TOPIC'] + b"ping/", "%s" % ping_mqtt)
        print("Send MQTT ping (%i)" % ping_mqtt)
        ping_fail += 1

        if ping_fail >= config.CONFIG['CRIT_MQTT_ERR']:
            print("MQTT ping false... reset (%i)" % ping_fail)
            machine.reset()

        if ping_fail >= config.CONFIG['MAX_MQTT_ERR']:
            print("MQTT ping false... reconnect (%i)" % ping_fail)
            client.disconnect()
            mqtt_reconnect()


# MQTT reconnect
def mqtt_reconnect():
    global client
    global ping_fail
    try:
        client = MQTTClient(config.CONFIG['CLIENT_ID'], config.CONFIG['MQTT_BROKER'], user=config.CONFIG['USER'],
                        password=config.CONFIG['PASSWORD'], port=config.CONFIG['PORT'])
        client.DEBUG = True
        client.set_callback(on_message)
        client.connect(clean_session=True)
        client.subscribe(config.CONFIG['TOPIC'] + b"#")
        print("ESP8266 is Connected to %s and subscribed to %s topic" % (
            config.CONFIG['MQTT_BROKER'], config.CONFIG['TOPIC'] + b"#"))
    except Exception as e:
        print("Error in mqtt reconnection: [Exception] %s: %s" % (type(e).__name__, e))


# Check MQTT message
async def check_message():
    while True:
        await asyncio.sleep_ms(1000)
        print("Check message...")
        try:
            client.check_msg()
        except Exception as e:
            print("Error in mqtt check message: [Exception] %s: %s" % (type(e).__name__, e))


# Check Internet connected
async def check_internet():
    global int_err_count
    try:
        while True:
            await asyncio.sleep_ms(10000)
            if not internet_connected():
                print("Internet connect fail...")
                int_err_count += 1

                if int_err_count >= config.CONFIG['CRIT_INT_ERR']:
                    client.disconnect()
                    wifi.wlan.disconnect()
                    machine.reset()

                if int_err_count >= config.CONFIG['MAX_INT_ERR']:
                    print("Internet reconnect")
                    client.disconnect()
                    wifi.wlan.disconnect()
                    wifi.activate()
    except Exception as e:
        print("Error in Internet connection: [Exception] %s: %s" % (type(e).__name__, e))


mqtt_reconnect()
try:
    loop = asyncio.get_event_loop()
    loop.create_task(check_sensor())
    loop.create_task(check_message())
    loop.create_task(check_internet())
    loop.create_task(send_mqtt_ping())
    loop.run_forever()
except Exception as e:
    print("Error: [Exception] %s: %s" % (type(e).__name__, e))
    time.sleep(60)
    machine.reset()
