from machine import Pin


class Tap:

    def __init__(self, pin):
        self.pin = pin

    def open(self):
        Pin(self.pin, Pin.OUT).high()
        return "Tap on pin %s is open" % self.pin

    def close(self):
        Pin(self.pin, Pin.OUT).low()
        return "Tap on pin %s is closed" % self.pin
#