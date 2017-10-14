from machine import Pin


class Tap:

    def __init__(self, pin):
        self.pin = pin

    def open(self):
        Pin(self.pin, Pin.OUT, value = 1)
        return "Tap on pin %s is open" % self.pin

    def close(self):
        Pin(self.pin, Pin.OUT, value = 0)
        return "Tap on pin %s is closed" % self.pin

