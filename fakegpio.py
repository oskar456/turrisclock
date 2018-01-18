#!/usr/bin/env python
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

from __future__ import print_function

class GPIO:
    """ Class representing one fake GPIO signal for debugging purposes """

    def __init__(self, name, direction="in"):
        """
        @param name GPIO number (224, 225, ...) as a string
        @direction string in or out
        """
        self.name = str(name)
        print("GPIO {} exported".format(name))
        self.reset()
        self.setDirection(direction)

    def __del__(self):
        """ Make sure direction is set to in to protect the SoC """
        self.setDirection("in")


    def setDirection(self, direction):
        """Sets pin direction"""
        self.direction = direction
        print("GPIO {} direction set to {}".format(self.name, direction))

    def get(self):
        """Return current GPIO value"""
        return False

    def set(self, value=True):
        """Sets GPIO to value"""
        print("GPIO {} set to {}".format(self.name, '1' if value else '0'))

    def reset(self):
        """Sets GPIO to value 0"""
        self.set(False)

    def __repr__(self):
        return "GPIO({}, {})".format(self.name, self.direction)
