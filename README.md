# Pi Power

**As of 09/23/2016 this is incomplete - I'm trying to get it finished but please don't go building a version of it until it's ready - please check back soon**

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
from Daniel Bull.

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


*Read on for details...*


# How it works

Starting with a powered down system, press the pushbutton and hold for a few seconds. The green activity LED on the Pi will start flickering to show
that the system is booting up. At that point you can release the pushbutton. You'll see the boot messages if you have a screen attached.

The two pi_power scripts will start up in background and the power status LEDs will indicate the current status.
These will change according to whether or not the USB power cable is connected and the current battery state.

You can safely shutdown the system manually by pressing the pushbutton again. The Pi will shutdown and the PowerBoost will stop providing power
to the Pi (the blue PowerBoost LED will go out). If the USB cable is connected, the battery will continue to recharge.

If you let the battery run out, the Red LED will warn you by flashing and when the fraction remaining reaches a low, but safe, level the system will
shutdown. The shutdown level is set conservatively to ensure the battery does not drain completely and cause the Pi to lose power.

# Hardware

The system uses a
[Adafruit PowerBoost 1000 Charger - Rechargeable 5V Lipo USB Boost @ 1A - 1000C](https://www.adafruit.com/products/2465)
to provide regulated 5V power from a LiPoly battery or a USB power supply. When a USB power supply is attached, the PowerBoost not
only powers the RasPi but also recharges the battery. It is a great little device for this sort of project. Adafruit sell it
for around $20 and they have a detailed [tutorial](https://learn.adafruit.com/adafruit-powerboost-1000c-load-share-usb-charge-boost) available.

There are three parts to the circuitry

## Power On / Power Off Switch

A momentary pushbutton switch is used to power up the Pi from a cold start and to trigger an orderly shutdown of the system.
This machinery is taken from the [LiPoPi](https://github.com/NeonHorizon/lipopi) project
from Daniel Bull, which I contributed to. Here is a description of how that works.

Pre-RasPi 3 circuit

![Power On / Power Off - schematic](/images/pi_power_schematic_1.png)

To power up from a cold start using the push button:

* The push button pulls the PowerBoost Enable pin high
* The PowerBoost delivers power to the Pi which starts to boot
* GPIO14 on the Pi goes high without any software being run
* GPIO14 keeps the PowerBoost Enable pin high when the push button is released

To shutdown safely using the push button:

* The pi_power.py script monitors GPIO26
* Pressing the push button sends this pin high and the script triggers a safe shutdown
* Shutdown means that GPIO14 is no longer high and so the PowerBoost stops sending power to the Pi
* The diodes isolate the power up and power down functions
* The two diodes in series serve to drop the battery voltage to a safe level for the Pi GPIO pin

Note that it leaves out the low battery component of that project as we can monitor that as part of the
battery voltage in the next section.

Also note the addition of a 0.1uF ceramic capacitor between GPIO26 and Ground. Without this, GPIO26 would trigger a shutdown whenever
I plugged the USB power cable into the PowerBoost. I don't why this happens but it probably because of relatively
long wires on the breadboard acting as radio antennae and picking up some sort of spike when the USB cable was connected.
This was easily solved, however, by adding the capacitor to smooth out the line to GPIO26. Try it in your
configuration and if you don't need it then leave it out.

Important Note - RasPi 3 treats GPIO14 differently - see the circuit below for the necessary change

![Pi3 Power On / Power Off - schematic](/images/pi_power_schematic_power_on_off_pi3.png)


RasPi 3 circuit

*to be added*

The RasPi model 3 changed the way GPIO14 operates. There are two important changes to the approach:

Pre-RasPi3 the serial console that uses GPIO14 used a hardware UART and that is what led GPIO14 to be high.
RasPi 3 uses a software UART which does not do this. But we can emulate this by *enabling* the serial console in raspi-config
and adding a capacitor across the 100K resistor to smooth the voltage on GPIO14 and keep the PowerBoost Enable pin high.


1 Do not make the raspi-config change
2 Place a 100uF 10V electrolytic capacitor in parallel to the 100K resistor, as shown in this schematicc.

*to be added*


## Voltage Monitoring with an ADC

To assess how much power is left in a battery we can use the pins on the PowerBoost1000C.
The Pi does not have an [Analog to Digital Converter](https://en.wikipedia.org/wiki/Analog-to-digital_converter) (ADC)
itself so we need to add an external one in the form of a [MCP3008](https://www.adafruit.com/products/856), which is an 8-Channel 10-Bit ADC With SPI Interface.
We are only using two channels so this is a bit of an overkill, but they are not expensive (around $4).

The **USB** pin on the PowerBoost has the voltage of the input USB connection. When the cable is not connected this is 0V and around 5.2V when connected.
Nominally, a USB power supply provides 5V but manufacturers often bump this up a little bit to counteract any voltage drop over
the supply cables.

The measured USB voltage is used to determine if the cable is attached or not. Doing this via an ADC is overkill but
as we need the ADC for the battery voltage, it makes sense to use it.


The Battery voltage on the **Bat** pin is what really tells us the current battery status. This has the output voltage of the LiPoly battery,
which varies from 3.7V when depleted to around 4.2V when fully charged.

The maximum input voltage for the analog side of the ADC is 3.3V so we need to reduce the PowerBoost voltages using a
pair of resistors acting as a [Voltage Divider](https://en.wikipedia.org/wiki/Voltage_divider). In this case a combination of 6.8K and 10K resistors
brings the maximum input voltages into the desired range.

The ADC uses the SPI interface on the RaspberryPi side which uses four GPIO pins. The code for this interface was written by the Adafruit
team and manages SPI in software, as opposed to the Pi's hardware SPI interface, so you can choose other GPIO pins if necessary.

![Battery monitor ADC - schematic](/images/pi_power_schematic_2.png)

**Note that this is a schematic and does not correspond to the actual chip pinout.**


## Battery Status LEDs

The system needs a way to tell the user how much power remains in the battery. One of the simplest ways is to control a Red and Green LED
from the RasPi to implement a simple interface - green is good, red means low battery.

![Status LEDs - schematic](/images/pi_power_schematic_3.png)




## Putting it all together

Wiring all this up on a breadboard gets you something like this:

![Breadboard](/images/pi_power_breadboard_small.png)

Here is a larger version of this [layout](https://github.com/craic/pi_power/images/pi_power_breadboard.png)

And here is what my actual breadboard looks like - not pretty, but functional

![Breadboard Photo](/images/breadboard_photo.jpg)

The breadboard layout was created to make the circuit easy to understand (you may argue whether or not I succeeded...).
One consequence of that is that a number of the jumper wires are relatively long, compared to a compact circuit board.
This may have a couple of unwanted side effects.

Long wires attached to RasPi GPIO pins may act as radio aerials. Even though the code uses internal pull-down resistors to avoid the pins from floating,
I did have a problem with the shutdown pin (GPIO26 in the circuit) getting triggered when I plugged the PowerBoost 1000C input USB
cable back in, after it had been disconnected.
I solved that by placing a 0.1uF ceramic capacitor between GPIO26 and Ground.

In addition, there can be voltage drop over longer wires and the breadboard tracks. The Adafruit guide to the PowerBoost 1000C mentions this.
*Shorter wires are better*


Please do not just wire your circuit from the breadboard diagram - *understand the circuit first* - you may be able to come up with a neater layout and,
more importantly, I may have made a mistake in creating the diagram.

# Software

*incomplete...*

The software end of Pi Power is split into two components.

The first one does all the work. [pi_power.py](pi_power.py) monitors the battery, handles the power down process as
well as shutting down the Pi is the battery runs out. It checks the battery every minute and records the current status
in the file /home/pi/.pi_power_status.

You can tun it with --debug or --log options if you want to capture the voltage changes over time, but it general it
is intended to run as a background process that starts up automatically when the Pi boots up.


There are many ways to inform the user about the power status. You might have a numeric display on a screen, or a bar graph
like you get on some phones. Separating the monitoring and display components makes it easier for others to build
different displays.

I have chosen the simple approach here of using a Red and Green LED to indicate the general power status.
[pi_power_leds.py](pi_power_leds.py) checks the status file and sets either led according to that.
It is easy to change the specific LED patterns but the default ones are:

* Green, Blinking - USB power source is connected - Battery is charging
* Green, Constant - Battery - more than 25% of battery remains
* Red, Constant - Battery - more than 15% of battery remains
* Red, Blinking - Battery - more than 10% of battery remains
* Red, Blinking Fast - Battery - less than 10% of battery remains - system will shutdown soon

Here is a plot of battery voltage over time, marked to show how the LED modes correspond to voltage.

![Status LEDs - schematic](/images/battery_voltage_graph.png)

The script checks the status file every 30 seconds so there can be a delay between, say, plugging in a USB supply and the LEDs
updating. Reducing the poll interval would improve this.

# Installation

Both scripts are intended to be run as silent background processes that start up when the Pi boots.

One location for these would be /etc/rc.local


**NOTE** The Pi boot process is different from other Linux systems in that there is no single-user mode. That
makes it difficult to fix problems in start up scripts like this as you have no easy way to run the system
up to, but not including, the problem script. *So... test everything really well before you put them in a
system start up script*


*to be added...*




# Notes

Please take a look at the [Wiki](https://github.com/craic/pi_power/wiki/Pi-Power-Wiki) for more background on battery charging, power usage by the Pi etc.


The power on / power off machinery is taken from the [LiPoPi](https://github.com/NeonHorizon/lipopi) project from Daniel Bull, which I have contributed to.
If you want a simpler solution without the voltage monitoring machinery then LiPoPi might be just what you need.



Use raspiconfig for older Pis...

Add the fix for Pi 3 etc...

Currently there is no way for the software to know when the battery is fully charged. On the PowerBoost, the yellow charging LED changes to Green, so
the information is available. There is just no easy way to get it to the Pi. Accurately estimating it from the voltage does not seem to work
well in practice.






