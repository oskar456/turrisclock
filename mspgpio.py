#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with


class MSP430:
    """Interfacing with MSP430 via /dev/ttyACM0"""

    def __init__(self):
        self.state = 0
        self.acm = open("/dev/ttyACM0", 'wb', 0)
        self._update()

    def __del__(self):
        self.acm.close()

    def _update(self):
        self.acm.write("{:01x}".format(self.state))

    def set(self, gpioid, value):
        """ Set GPIO with given ID (bit weight) to given value """
        if value:
            self.state |= gpioid
            self.state %= 4
        else:
            self.state &= ~gpioid
            self.state %= 4
        if gpioid == 1:
            self._update()


msp = MSP430()


class GPIO:
    """ Class representing one GPIO signal """

    def __init__(self, name, direction="in"):
        """
        @param name GPIO number (224, 225, ...) as a string
        @direction string in or out
        """
        self.name = str(name)
        self.msp = msp
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
        self.msp.set(1 if self.name=="225" else 2, value)

    def reset(self):
        """Sets GPIO to value 0"""
        self.set(False)

    def __repr__(self):
        return "GPIO({}, {})".format(self.name, self.direction)

