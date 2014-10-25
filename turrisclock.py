#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

from gpio import GPIO
from clock import Clock
from statestore import StateStore
import signal
import time


if __name__ == "__main__":

    def killhandler(signum, frame):
        raise RuntimeError("Killed")

    import argparse

    parser = argparse.ArgumentParser(description='TurrisClock')
    parser.add_argument("--invert", action='store_true')
    parser.add_argument("--uninvert", action='store_true')
    parser.add_argument("--state", help='hh:mm:ss')
    parser.add_argument("--comfortstep", "-c", help='Comfort step interval when waiting', default=10, type=int, choices=xrange(0, 3600))
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
            if nowstate == clock.state:
                time.sleep(1 - now%1) #wait for the end of current second
            else:
                # In case clock is too fast, it's wise to wait a bit
                if clock.stepstogo(nowstate) > 40000:
                    towait = clock.timetowait(nowstate, args.comfortstep)
                    if clock.timetogo(nowstate) > towait:
                        # waiting for the time, with comfort step every 10 seconds
                        time.sleep(args.comfortstep - now%args.comfortstep \
                                   if towait > args.comfortstep else towait + 1 - now%1)
                clock.step()
    finally:
        statestore.save()
