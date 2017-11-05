from machine import Pin


class Tap:

    def __init__(self, pin_s, pin_d):
        self.pin_s = pin_s
        self.pin_d = pin_d

    def open(self):
        Pin(self.pin_s, Pin.OUT, value = 1)
        Pin(self.pin_d, Pin.OUT, value = 1)
        return "Tap on pin %s is open" % self.pin_d

    def close(self):
        Pin(self.pin_s, Pin.OUT, value = 1)
        Pin(self.pin_d, Pin.OUT, value = 0)
        return "Tap on pin %s is closed" % self.pin_d

