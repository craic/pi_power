# pi_power

** As of 09/23/2016 this is incomplete - I'm trying to get it finished - please check back soon **

The [Raspberry Pi](https://www.raspberrypi.org/) is a low cost, single board computer with reasonable performance and relatively low power
consumption. They are typically configured with the Linux operating system, often with [Raspbian](https://www.raspberrypi.org/downloads/raspbian/).

The Pi family of boards have turned out to be very useful machines for standalone and/or
portable projects such as remote environment monitoring, cameras, etc.

But to be truly portable, a system needs to include a power source and a way to control
that power - such as a rechargeable battery, a charger, an on/off switch and some
way to monitor battery status.

What I want is something equivalent to the way my iPhone works.
- I power it up from a cold state by holding down a button for a few seconds.
- To power it off I press the same button for a few seconds
- The screen has an icon that shows me how much power remains in the battery
- I get an alert when that is running really low.
- If the battery runs out then the phone shuts down safely without any data corruption.
- To recharge the battery I just plug in a cable from a USB charger.


A number of people have worked on pieces of this puzzle but I have yet to see a complete
solution. This project is my attempt at one.


Please take a look at the [Wiki](https://github.com/craic/pi_power/wiki/Pi-Power-Wiki) for more background.


This system consists of some relatively simple circuitry that links the Pi with an Adafruit PowerBoost 1000C LiPoly charger
and some two Python scripts.

pi_power.py monitors the battery voltage and handles shutdown of the system
when the battery runs out, or when the user pushes a button. It writes the current battery status to a file.

pi_power_leds.py checks the status file and sets a red or green led according to that.


The hardware looks like this:

![Power On / Power Off - schematic](/images/pi_power_schematic_1.png)


![Battery monitor ADC - schematic](/images/pi_power_schematic_2.png)


![Status LEDs - schematic](/images/pi_power_schematic_3.png)



![Breadboard](/images/pi_power_breadboard_small.png)

Here is a larger version of this [layout](https://github.com/craic/pi_power/images/pi_power_breadboard.png)



The software consists of two python scripts:

pi_power.py

This monitors the ADC and the pushbutton and updates the power status file.

pi_power_leds.py

This checks the power status file and sets one of two LEDs accordingly.




# Notes

The power on / power off machinery is taken from the [LiPoPi](https://github.com/NeonHorizon/lipopi) project from Daniel Bull, which I have contributed to.

The breadboard layout was created to make the circuit easy to understand (you may argue whether or not I succeeded in that!).
One consequence of that is that a number of the jumper wires are relatively long, compared to a compact circuit board.
This may have a couple of unwanted side effects.

Long wires attached to RasPi GPIO pins may act as radio aerials. Even though the code uses internal pull-down resistors to avoid the pins from floating,
I did have a problem with the shutdown pin (GPIO26 in the circuit) getting triggered when I plugged the PowerBoost 1000C input USB
cable back in, after it had been disconnected.
I solved that by placing a 0.1uF ceramic capacitor between GPIO26 and Ground.

Please do not just wire your circuit from the breadboard diagram - understand the circuit first - you may be able to come up with a neater layout.
More importantly, I may have made a mistake in cerating the diagram.







