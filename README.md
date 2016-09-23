# pi_power

** As of 09/23/2016 this is incomplete - I'm trying to get it finished - please check back soon **

The [Raspberry Pi](https://www.raspberrypi.org/) is a low cost, single board computer with reasonable performance and relatively low power
consumption. They are typically configured with the Linux operating system, often with [Raspbian](https://www.raspberrypi.org/downloads/raspbian/).

The Pi family of boards have turned out to be very useful machines for standalone and/or
portable projects such as remote environment monitoring, cameras, etc.

But in order to be truly portable, a system needs to include a power source and a way to control
that power - such as a rechargeable battery, a charger, an on/off switch and some
way to monitor battery status.

What I want is something equivalent to the way my iPhone works.
- I power it up from a cold state by holding down a button for a few seconds.
- To power it off I press the same button for a few seconds (and swipe an alert on the screen)
- The screen has an icon that shows me how much power remains in the battery
- I get an alert when that is running really low.
- If the battery runs out then the phone shuts down safely without any data corruption.
- To recharge the battery I just plug in a cable from a USB charger.


A number of people have worked on pieces of this puzzle but I have yet to see a complete
solution. This repository documents my attempt to reach this goal.

Please take a look at the [Wiki](https://github.com/craic/pi_power/wiki/Pi-Power-Wiki) for more background.

This system consists of some relatively simple circuitry that links the Pi with an Adafruit PowerBoost 1000C LiPoly charger
and some software that runs on the Pi to monitor battery status.

The hardware looks like this:

![Power On / Power Off - schematic](/images/pi_power_schematic_1.png)


![Battery monitor ADC - schematic](/images/pi_power_schematic_2.png)


![Status LEDs - schematic](/images/pi_power_schematic_3.png)



![Breadboard](/images/pi_power_breadboard_small.png)

Here is a larger version of this [layout](https://github.com/craic/pi_power/images/pi_power_breadboard_small.png)

The software consists of two python scripts:

pi_power.py

This monitors the ADC and the pushbutton and updates the power status file.

pi_power_leds.py

This checks the power status file and sets one of two LEDs accordingly.










