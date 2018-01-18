#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

import time
import re


class Clock:
    """ Class representing clock state """

    ontime = 0.038   # on pulse width
    offtime = 0.022  # minimum off time after pulse
    state = 0       # current state of the movement (0..43199)
    inverse = False # inversed polarity signal

    @staticmethod
    def statetohours(state):
        """ Converts clock state to a tuple (hour, min, secs) """
        state = int(state)
        hours = state // 3600
        hours = 12 if hours==0 else hours
        mins  = (state % 3600) // 60
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

    @property
    def stepduration(self):
        return self.ontime + self.offtime

    def stepstogo(self, desiredstate):
        """ Calculates number of steps needed to reach desired state """
        # Add 43200 to left side to avoid negative numbers when wrapping over
        steps = ((43200+desiredstate) - self.state) % 43200
        # In case desired state == current state, return full scale instead of 0
        return 43200 if steps<1 else steps

    def timetogo(self, desiredstate):
        """ Calculates approx. time needed to reach desired state """
        # Sum of infinite geometric series with a1 = stepstogo*stepduration
        # and q = stepduration
        return self.stepduration * self.stepstogo(desiredstate)/(1-self.stepduration)

    def timetowait(self, desiredstate, comfortsteps=10):
        """
        Calculates approx. time to wait until desired state becomes current state.
        A step every comfortsteps seconds can be added to calm down the user
        """
        timetowait = ((43200+self.state) - int(desiredstate)) % 43200
        if comfortsteps > 1:
            # This is actually a sum of infinite geometric series
            # with a1=timetowait and q=1/comfortsteps
            # Sum is therefore a1/(1-q)
            timetowait = timetowait*comfortsteps/(comfortsteps-1)
        return timetowait


    def __str__(self):
        return "Clock <{}> Inversed: {}".format(self.getState(), self.inverse)

    def __repr__(self):
        return "Clock({}, {}, {}, {})".format(self.CLK, self.POL, self.state, self.inverse)


def test():
    clock = Clock(None, None)
    print clock
    clock.setState("13:23:4")
    print clock.getState()
    newstate = Clock.parsestate("12:43:04")
    print "Time to go: ", clock.timetogo(newstate)
    print "Time to wait: ", clock.timetowait(newstate)
    print repr(clock)


if __name__ == "__main__":
    test()
