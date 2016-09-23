# pi_power

**As of 09/23/2016 this is incomplete - I'm trying to get it finished - please check back soon**

The [Raspberry Pi](https://www.raspberrypi.org/) is a low cost, single board computer with reasonable performance and relatively low power
consumption, typically a version of the Linux operating system, often [Raspbian](https://www.raspberrypi.org/downloads/raspbian/).

The Pi family of boards have turned out to be very useful machines for standalone and/or
portable projects such as remote environment monitoring, cameras, etc.

But to be truly portable, a system needs to include a power source and a way to control
that power - such as a rechargeable battery, a charger, an on/off switch and some
way to monitor battery status.

What I want is something equivalent to the way my iPhone works
- To power it up from a cold state, press a button for a few seconds
- To power it off, press the same button for a few seconds
- Indicate how much power remains in the battery
- Provide an alert when that is running really low
- Shut down safely without any data corruption if the battery does run out
- To recharge the battery, just plug in a cable from a USB charger


This project provides one approach to reaching this goal, building on the [LiPoPi](https://github.com/NeonHorizon/lipopi) project
from Daniel Bull, which I have contributed to.

# Overview

The system consists of some relatively simple circuitry that links the Pi with a LiPoly battery charger
and two Python scripts that handle monitoring and control.



The **hardware** looks like this:

![Power On / Power Off - schematic](/images/pi_power_schematic_1.png)


![Battery monitor ADC - schematic](/images/pi_power_schematic_2.png)


![Status LEDs - schematic](/images/pi_power_schematic_3.png)



The **software** consists of two python scripts:

[pi_power.py](pi_power.py) monitors the battery voltage and handles shutdown of the system
when the battery runs out, or when the user pushes a button. It writes the current battery status to a file.

[pi_power_leds.py](pi_power_leds.py) checks the status file and sets a red or green led according to that.





# Hardware

The system uses a
[Adafruit PowerBoost 1000 Charger - Rechargeable 5V Lipo USB Boost @ 1A - 1000C](https://www.adafruit.com/products/2465)
to provide regulated 5V power from a LiPoly battery or a USB power supply. When a USB power supply is attached, the PowerBoost not
only powers the RasPi but also recharges the battery. It is a great little device for this sort of project.

There are three parts to the circuitry

A momentary pushbutton switch is used to power up the Pi from a cold start and to trigger an orderly shutdown of the system.
This machinery is taken from the [LiPoPi](https://github.com/NeonHorizon/lipopi) project
from Daniel Bull.

![Power On / Power Off - schematic](/images/pi_power_schematic_1.png)





Wiring all this up on a breadboard gets you something like this:

![Breadboard](/images/pi_power_breadboard_small.png)

Here is a larger version of this [layout](https://github.com/craic/pi_power/images/pi_power_breadboard.png)

And here is what my actual breadboard looks like - not pretty, but functional

![Breadboard Photo](/images/breadboard_photo.jpg)



# Notes

Please take a look at the [Wiki](https://github.com/craic/pi_power/wiki/Pi-Power-Wiki) for more background.


The power on / power off machinery is taken from the [LiPoPi](https://github.com/NeonHorizon/lipopi) project from Daniel Bull, which I have contributed to.

The breadboard layout was created to make the circuit easy to understand (you may argue whether or not I succeeded in that!).
One consequence of that is that a number of the jumper wires are relatively long, compared to a compact circuit board.
This may have a couple of unwanted side effects.

Long wires attached to RasPi GPIO pins may act as radio aerials. Even though the code uses internal pull-down resistors to avoid the pins from floating,
I did have a problem with the shutdown pin (GPIO26 in the circuit) getting triggered when I plugged the PowerBoost 1000C input USB
cable back in, after it had been disconnected.
I solved that by placing a 0.1uF ceramic capacitor between GPIO26 and Ground.

In addition, there can be voltage drop over longer wires and the breadboard tracks. The Adafruit guide to the PowerBoost 1000C mentions this. Shorter wires are better.


Please do not just wire your circuit from the breadboard diagram - understand the circuit first - you may be able to come up with a neater layout.
More importantly, I may have made a mistake in cerating the diagram.

Use raspiconfig for older Pis...

Add the fix for Pi 3 etc...

Warning about systemd etc...





