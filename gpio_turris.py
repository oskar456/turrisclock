#!/usr/bin/env python
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

import turris_gpio as gpio
gpio.setmode(gpio.SOC)

class GPIO:
    """ Class representing one GPIO signal """

    def __init__(self, name, direction="in"):
        """
        @param name GPIO number (480, 481, ...)
        @direction string in or out
        """
        self.pin = int(name) - 480
        self.setDirection(direction)
        self.reset()

    def __del__(self):
        """ Make sure direction is set to in to protect the SoC """
        self.setDirection("in")

    def setDirection(self, direction):
        """Sets pin direction"""
        self.direction = direction
        d = gpio.OUT if direction == "out" else gpio.IN
        gpio.setup(self.pin, d)

    def get(self):
        """Return current GPIO value"""
        return gpio.input(self.pin)

    def set(self, value=True):
        """Sets GPIO to value"""
        gpio.output(self.pin, value)

    def reset(self):
        """Sets GPIO to value 0"""
        self.set(False)

    def __repr__(self):
        return "GPIO({}, {})".format(self.name, self.direction)

