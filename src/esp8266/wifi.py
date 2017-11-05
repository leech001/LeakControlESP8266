import network


def activate():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('WIFI_NET', 'pass')
        while not wlan.isconnected():
            pass
        print('network config:', wlan.ifconfig())

