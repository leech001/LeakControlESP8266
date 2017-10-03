import network

def activate():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('H37-WIFI', 'Secret2017')
        while not wlan.isconnected():
            pass
        print('network config:', wlan.ifconfig())
#