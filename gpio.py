#!/usr/bin/env python
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

class GPIO:
    """ Class representing one GPIO signal """

    def __init__(self, name, direction="in"):
        """
        @param name GPIO number (224, 225, ...) as a string
        @direction string in or out
        """
        self.name = str(name)
        with open("/sys/class/gpio/export", 'w') as f:
            f.write(self.name)
        self.sysfspath = "/sys/class/gpio/gpio{}/".format(self.name)
        self.reset()
        self.setDirection(direction)

    def __del__(self):
        """ Make sure direction is set to in to protect the SoC """
        self.setDirection("in")

    def setDirection(self, direction):
        """Sets pin direction"""
        self.direction = direction
        with open("{}/direction".format(self.sysfspath), 'w') as f:
            f.write(direction)

    def get(self):
        """Return current GPIO value"""
        with open("{}/value".format(self.sysfspath), 'r') as f:
            return True if f.read(1) == "1" else False

    def set(self, value=True):
        """Sets GPIO to value"""
        with open("{}/value".format(self.sysfspath), 'w') as f:
            f.write("1" if value else "0")

    def reset(self):
        """Sets GPIO to value 0"""
        self.set(False)

    def __repr__(self):
        return "GPIO({}, {})".format(self.name, self.direction)

