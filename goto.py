#!/usr/bin/env python3
# vim: expandtab shiftwidth=4 tabstop=8 softtabstop=4 smartindent cinwords=if,elif,else,for,while,try,except,finally,def,class,with

from turrisclock import Clock, argument_parser, clockinit

if __name__ == "__main__":
    parser = argument_parser(description='TurrisClock goto')
    parser.add_argument("destination", help='hh:mm:ss to reach')
    args = parser.parse_args()
    clock, statestore, nvramstore = clockinit(args)
    deststate = Clock.parsestate(args.destination)

    try:
        while clock.state != deststate:
            clock.step()
            nvramstore.save()
    finally:
        statestore.save()
