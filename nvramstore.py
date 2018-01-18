#!/usr/bin/env python
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

from __future__ import print_function
import sys
import struct


class NVRAMStore:
    """ Store for save and restore clock state """
    MAGIC = "TRSCLK"
    fmt = struct.Struct("6sH")  # 6 byte magic plus one unsigned short

    def __init__(self, clock, filename="/sys/devices/platform/soc@ffe00000/"
                 "ffe03000.i2c/i2c-0/0-006f/nvram"):
        self.clock = clock
        self.filename = filename

    def save(self):
        """ Saves current state to file """
        try:
            with open(self.filename, 'wb') as f:
                f.write(self.fmt.pack(self.MAGIC, self.clock.state))
        except IOError:
            pass

    def restore(self):
        """ Restores current state from file """
        try:
            with open(self.filename, 'rb') as f:
                out = self.fmt.unpack(f.read(self.fmt.size))
            if out[0] == self.MAGIC:
                self.clock.state = out[1]
                return True
            else:
                print("Clock state restore failed: invalid magic")
        except:
            print("Clock state restore failed:", sys.exc_info()[1])
        return False
