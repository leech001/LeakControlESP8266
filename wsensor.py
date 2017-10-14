from machine import Pin


class WS:

    def __init__(self, pin):
        self.pin = pin

    def check(self):
        return Pin(self.pin, Pin.IN).value()

