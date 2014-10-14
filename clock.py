#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

import time
import re


class Clock:
    """ Class representing clock state """

    ontime = 0.03   # 30ms pulse width
    offtime = 0.022  # minimum off time after pulse
    state = 0       # current state of the movement (0..43199)
    inverse = False # inversed polarity signal

    @staticmethod
    def statetohours(state):
        """ Converts clock state to a tuple (hour, min, secs) """
        hours = state / 3600
        mins  = (state % 3600) / 60
        secs  = state % 60
        return (hours, mins, secs)

    @staticmethod
    def hourstostate(hours, mins, secs):
        """ Converts tuple (hour, min, secs) to a single number 
        representing clock state """
        return (3600*hours + 60*mins + secs) % 43200
    
    @staticmethod
    def statetostr(state):
        """ Returns the movement state as a string like 12:34:56 """
        return "{:02d}:{:02d}:{:02d}".format(*Clock.statetohours(state))

    @staticmethod
    def parsestate(statestr):
        """ Try to parse movement state from a string as 12:34:56 """
        m = re.search("([0-9]+):([0-9]+):([0-9]+)", statestr)
        if m:
            return Clock.hourstostate(*(int(s) for s in m.groups()))
        else:
            raise ValueError("movement state not found in string {}".format(statestr))


    def __init__(self, clock_signal, polarity_signal, state=0, inverse_polarity=False):
        """
        @param clock_signal GPIO representing
        """
        self.CLK = clock_signal
        self.POL = polarity_signal
        self.state = state
        self.inverse = inverse_polarity


    def step(self):
        """
        Generate one clock step, shift the movement one second ahead.
        """
        self.POL.set(self.inverse ^ (self.state & 0x01))
        self.CLK.set()
        self.state = (self.state + 1) % 43200
        time.sleep(self.ontime)
        self.CLK.reset()
        self.POL.reset()
        time.sleep(self.offtime)

    def getState(self):
        """ Returns current clock state as a string like 12:34:56 """
        return Clock.statetostr(self.state)

    def setState(self, statestr):
        """ Sets clock state from input string """
        self.state = Clock.parsestate(statestr)

    def __str__(self):
        return "Clock <{}> Inversed: {}".format(self.getState(), self.inverse)

    def __repr__(self):
        return "Clock({}, {}, {}, {})".format(self.CLK, self.POL, self.state, self.inverse)


if __name__ == "__main__":
    clock = Clock(None, None)
    print clock
    clock.setState("13:23:4")
    print clock.getState()
    print repr(clock)
