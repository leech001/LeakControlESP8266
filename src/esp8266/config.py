from tap import Tap
from wsensor import WS

ntp_delta = 3155673600
host = "pool.ntp.org"
tap_cold = Tap(5, 0, "ready")  # D1
tap_hot = Tap(4, 2, "ready")  # D2
ws = WS(14)  # Water sensor (pin)

# Modify below section as required
CONFIG = {
    "MQTT_BROKER": "x.x.x.x",
    "MQTT_USER": "user",
    "MQTT_PASSWORD": "pass",
    "MQTT_PORT": 1883,
    "MQTT_CLIENT_ID": "ESP_BIG_01",
    "MQTT_MAX_ERR": 5,
    "MQTT_CRIT_ERR": 10,
    "DEVICE_TYPE": "leak",
    "DEVICE_PLACE": "Home/66",
    "DEVICE_PLACE_TYPE": "bath",
    "DEVICE_PLACE_NAME": "big",
    "DEVICE_ID": "01",
    "DEVICE_ID_USE": "01",
    "WIFI_LOGIN": "WIFI_APP",
    "WIFI_PASSWORD": "WIFI_PASS",
    "INT_MAX_ERR": 20,
    "INT_CRIT_ERR": 50
}
