from tap import Tap
from wsensor import WS

ntp_delta = 3155673600
host = "pool.ntp.org"
tap_cold = Tap(5, 0)  # D1
tap_hot = Tap(4, 2)  # D2
ws = (WS(14), WS(12))  # Water sensor tuples (pin)

# Modify below section as required
CONFIG = {
    # Configuration details of the MQTT broker
    "MQTT_BROKER": "192.168.0.28",
    "USER": "",
    "PASSWORD": "",
    "PORT": 1883,
    "TOPIC": b"bath/big/",
    "CLIENT_ID": b"ESPython_big",
    "MAX_MQTT_ERR": 5,
    "CRIT_MQTT_ERR": 10,
    "MAX_INT_ERR": 20,
    "CRIT_INT_ERR": 50
}