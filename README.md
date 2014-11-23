TurrisClock
===========

Driving clock movement from the Turris Router.

See the [project page](http://oskar456.github.io/turrisclock/) for more informations.

This is a simple set of python scripts for driving hardware clock connected to GPIO pins of a computer
(like [Turris router](https://www.turris.cz/)). Two GPIO pins are used. First GPIO pin named CLK enables/disables
powering the step motor (0 = powered off, 1 = powered on). Second GPIO pin is used to control the polarity of
current flowing through the motor. In case the clock movement appears to be 1 second slow, you should
either swap wires connecting the step motor or activate polarity inversion in Clock class.
