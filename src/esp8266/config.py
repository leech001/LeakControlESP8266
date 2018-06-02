from tap import Tap
from wsensor import WS

ntp_delta = 3155673600
host = "pool.ntp.org"
tap_cold = Tap(5, 0)  # D1
tap_hot = Tap(4, 2)  # D2
ws = (WS(14), WS(12))  # Water sensor tuples (pin)

# Modify below section as required
CONFIG = {
    "MQTT_BROKER": "x.x.x.x",
    "MQTT_USER": "user",
    "MQTT_PASSWORD": "pass",
    "MQTT_PORT": 31883,
    "MQTT_CLIENT_ID": "ESP_BIG_01",
    "MQTT_MAX_ERR": 5,
    "MQTT_CRIT_ERR": 10,
    "DEVICE_TYPE" : "leak",
    "DEVICE_PLACE" : "bath",
    "DEVICE_PLACE_NAME" : "big",
    "DEVICE_ID": "01",
    "DEVICE_ID_USE": "01",
    "WIFI_LOGIN" : "user",
    "WIFI_PASSWORD" : "pass",
    "INT_MAX_ERR": 20,
    "INT_CRIT_ERR": 50
}
