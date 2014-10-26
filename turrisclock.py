#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

from mspgpio import GPIO
from clock import Clock
from statestore import StateStore
import signal
import time


if __name__ == "__main__":

    def killhandler(signum, frame):
        raise RuntimeError("Killed")

    import argparse

    def pos_int(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise argparse.ArgumentTypeError("{} is an invalid positive int value".format(value))
        return ivalue

    parser = argparse.ArgumentParser(description='TurrisClock')
    parser.add_argument("--invert", action='store_true')
    parser.add_argument("--uninvert", action='store_true')
    parser.add_argument("--state", help='hh:mm:ss')
    parser.add_argument("--step", "-s", help='step interval', default=1, type=pos_int)
    parser.add_argument("--comfortstep", "-c", help='comfort step interval when waiting', default=10, type=pos_int)
    args = parser.parse_args()


    CLK = GPIO("224", "out")
    POL = GPIO("225", "out")
    clock = Clock(CLK, POL)
    statestore = StateStore(clock)
    statestore.restore()

    if args.invert:
        clock.inverse = True

    if args.uninvert:
        clock.inverse = False

    if args.state:
        clock.setState(args.state)

    signal.signal(signal.SIGTERM, killhandler)

    try:
        while True:
            now = time.time()
            nows = time.localtime(now)
            nowstate = Clock.hourstostate(nows.tm_hour, nows.tm_min, nows.tm_sec)
            # In case clock is too fast, it's wise to wait a bit
            towait = clock.timetowait(nowstate, args.comfortstep) \
                     + args.step - now%args.step
            if clock.timetogo(nowstate) > towait:
                # waiting for the time, with comfort step every few seconds
                time.sleep(args.comfortstep - now%args.comfortstep \
                           if towait > args.comfortstep > 1 \
                           else towait)
            clock.step()
    finally:
        statestore.save()
