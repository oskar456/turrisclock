#!/usr/bin/env python2.7
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

from gpio import GPIO
from clock import Clock
from statestore import StateStore
from nvramstore import NVRAMStore
import signal
import time
import argparse

def killhandler(signum, frame):
    raise RuntimeError("Killed")

signal.signal(signal.SIGTERM, killhandler)

def pos_int(value):
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("{} is an invalid positive int value".format(value))
    return ivalue

def argument_parser(description='TurrisClock'):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--invert", action='store_true')
    parser.add_argument("--uninvert", action='store_true')
    parser.add_argument("--state", help='hh:mm:ss')
    return parser

def clockinit(args):
    POL = GPIO("480", "out")
    CLK = GPIO("481", "out")
    clock = Clock(CLK, POL)
    statestore = StateStore(clock)
    statestore.restore()
    nvramstore = NVRAMStore(clock)
    nvramstore.restore()
    if args.invert:
        clock.inverse = True
    if args.uninvert:
        clock.inverse = False
    if args.state:
        clock.setState(args.state)
    return (clock, statestore, nvramstore)

if __name__ == "__main__":


    parser = argument_parser(description='TurrisClock')
    parser.add_argument("--step", "-s", help='step interval', default=1, type=pos_int)
    parser.add_argument("--comfortstep", "-c", help='comfort step interval when waiting', default=10, type=pos_int)
    args = parser.parse_args()
    if args.step > args.comfortstep:
        args.comfortstep = args.step
    clock, statestore, nvramstore = clockinit(args)

    def usr1handler(signum, frame):
        clock.state -= 2

    signal.signal(signal.SIGUSR1, usr1handler)

    try:
        while True:
            now = time.time()
            nows = time.localtime(now)
            nowstate = Clock.hourstostate(nows.tm_hour, nows.tm_min, nows.tm_sec) + now%1

            if nowstate//args.step == clock.state//args.step:
                time.sleep(args.step - nowstate%args.step)
            else:
                towait = clock.timetowait(nowstate, args.comfortstep) \
                         + args.step - nowstate%args.step
                if clock.timetogo(nowstate) > towait:
                    # waiting for the time, with comfort step every few seconds
                    time.sleep(args.comfortstep - nowstate%args.comfortstep \
                               if towait > args.comfortstep > 1 \
                               else towait)
                clock.step()
                nvramstore.save()
    finally:
        statestore.save()
