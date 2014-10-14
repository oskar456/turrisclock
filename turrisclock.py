#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

import time
import re
import sys
import signal
import os

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


class FakeGPIO:
    """ Class representing one fake GPIO signal for debugging purposes"""

    def __init__(self, name, direction="in"):
        """
        @param name GPIO number (224, 225, ...) as a string
        @direction string in or out
        """
        self.name = str(name)
        print "GPIO {} exported".format(name)
        self.reset()
        self.setDirection(direction)

    def __del__(self):
        """ Make sure direction is set to in to protect the SoC """
        self.setDirection("in")


    def setDirection(self, direction):
        """Sets pin direction"""
        self.direction = direction
        print "GPIO {} direction set to {}".format(self.name, direction)

    def get(self):
        """Return current GPIO value"""
        return False

    def set(self, value=True):
        """Sets GPIO to value"""
        print "GPIO {} set to {}".format(self.name, '1' if value else '0')

    def reset(self):
        """Sets GPIO to value 0"""
        self.set(False)

    def __repr__(self):
        return "FakeGPIO({}, {})".format(self.name, self.direction)


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
        """ Returns current clock state as a tuple (hour, min, secs) """
        return Clock.statetohours(self.state)

    def setState(self, hours, mins, secs):
        """ Sets clock state """
        self.state = Clock.hourstostate(hours, mins, secs)

    def __str__(self):
        h, m, s = self.getState()
        return "Clock <{}:{}:{}> Inversed: {}".format(h, m, s, self.inverse)

    def __repr__(self):
        return "Clock({}, {}, {}, {})".format(self.CLK, self.POL, self.state, self.inverse)

class StateStore:
    """ Store for save and restore clock state """
    def __init__(self, clock, filename="/root/clockstate.txt"):
        self.clock = clock
        self.filename = filename
    
    def save(self):
        """ Saves current state to file """
        with open(self.filename, 'w') as f:
            h, m, s = self.clock.getState()
            f.write("{}:{}:{}\n".format(h, m, s))
            f.write("Reverse polarity: {}\n".format(self.clock.inverse))

    def restore(self):
        """ Restores current state from file """
        try:
    
            with open(self.filename, 'r') as f:
                timestring = f.readline()
                m = re.match("([0-9]+):([0-9]+):([0-9]+)", timestring)
                if m:
                    self.clock.setState(*(int(s) for s in m.groups()))
                else:
                    raise ValueError("No timestring found")
                invstring = f.readline()
                m = re.match("Reverse polarity: True", invstring)
                if m:
                    self.clock.inverse = True
        except:
            print "Clock state restore failed:", sys.exc_info()[0]



    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='TurrisClock')
    parser.add_argument("--invert", action='store_true')
    parser.add_argument("--state", help='hh:mm:ss')
    args = parser.parse_args()


    CLK = GPIO("224", "out")
    POL = GPIO("225", "out")
    clock = Clock(CLK, POL)
    statestore = StateStore(clock)
    statestore.restore()

    clock.inverse = args.invert

    if args.state:
        m = re.search("([0-9]+):([0-9]+):([0-9]+)", args.state)
        if m:
            clock.setState(*(int(s) for s in m.groups()))

    def killhandler(signum, frame):
        raise RuntimeError("Killed")

    signal.signal(signal.SIGTERM, killhandler)

    try:
        while True:
            now = time.time()
            nows = time.localtime(now)
            nowstate = Clock.hourstostate(nows.tm_hour, nows.tm_min, nows.tm_sec)
            if nowstate == clock.state:
                time.sleep(1 - now%1) #wait for the end of current second
            else:
                clock.step()
    except:
        statestore.save()


