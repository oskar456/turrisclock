#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

import sys
import re

class StateStore:
    """ Store for save and restore clock state """
    def __init__(self, clock, filename="/root/clockstate.txt"):
        self.clock = clock
        self.filename = filename
    
    def save(self):
        """ Saves current state to file """
        with open(self.filename, 'w') as f:
            f.write(self.clock.getState())
            f.write("\nReverse polarity: {}\n".format(self.clock.inverse))

    def restore(self):
        """ Restores current state from file """
        try:   
            with open(self.filename, 'r') as f:
                self.clock.setState(f.readline())
                invstring = f.readline()
                m = re.match("Reverse polarity: True", invstring)
                if m:
                    self.clock.inverse = True
        except:
            print "Clock state restore failed:", sys.exc_info()[1]
