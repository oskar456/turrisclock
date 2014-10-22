TurrisClock
===========

Driving clock movement from Turris Router.

This is a simple set of python scripts for driving hardware clock connected to GPIO pins of a computer
(like [Turris router](https://www.turris.cz/)). Two GPIO pins are used. First GPIO pin named CLK enables/disables
powering the step motor (0 = powered off, 1 = powered on). Second GPIO pin is used to control polarity of the
current flowing through the motor. In case the clock movement appears to be 1 second slow or faster, you should
either swap wires from step motor or activate polarity inversion in Clock class.

Detailed specs will be published later.
