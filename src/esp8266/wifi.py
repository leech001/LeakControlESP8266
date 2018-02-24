import network
global wlan


def activate():
    global wlan
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('AP-NAME', 'AP-PASS')
        while not wlan.isconnected():
            pass
        print('network config:', wlan.ifconfig())
