#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

import time
class GPIO:
    """ Class representing one GPIO signal """

    def __init__(self, name, direction="in"):
        """
        @param name GPIO number (224, 225, ...) as a string
        @direction string in or out
        """
        self.name = str(name)
        self.onstring =  'A' if self.name == '224' else 'B'
        self.offstring = 'a' if self.name == '224' else 'b'
        self.path = "/dev/ttyACM0"
        self.reset()
        self.setDirection(direction)

    def __del__(self):
        """ Make sure direction is set to in to protect the SoC """
        self.setDirection("in")
        self.reset()

    def setDirection(self, direction):
        """Sets pin direction"""
        self.direction = direction

    def get(self):
        """Return current GPIO value"""

    def set(self, value=True):
        """Sets GPIO to value"""
        with open(self.path, 'w') as f:
            f.write(self.onstring if value else self.offstring)
        time.sleep(0.009)


    def reset(self):
        """Sets GPIO to value 0"""
        self.set(False)

    def __repr__(self):
        return "GPIO({}, {})".format(self.name, self.direction)

