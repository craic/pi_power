#!/usr/bin/env python

# pi_power_led.py

# Copyright (c) 2016 Robert Jones, Craic Computing LLC
# Freely distributed under the terms of the MIT License

# Read the contents of /home/pi/.pi_power_status and light red and green leds accordingly

# The default configuration for the LEDs is Common Anode which works for most RGB LEDs

# LED modes
# green blinking    - USB cable attached, charging battery
# green constant    - on battery, >= 0.5 fraction of battery life
# red constant      - on battery, < 0.20 fraction of battery life
# red blinking      - on battery, < 0.15 fraction of battery life
# red blinking fast - on battery, < 0.10 fraction of battery life

# .pi_power file format:
# one line - <battery fraction 0.0-1.0>,<power source - usb or battery>
# for example:
#1.00,usb
#0.50,battery


# Define each LED mode - set the on/off times here (in seconds) - 0 means always on
def green_constant():
    blink_time_on  = 0
    blink_time_off = 0
    leds = ['green']
    update_leds(leds, blink_time_on, blink_time_off)

def red_constant():
    blink_time_on  = 0
    blink_time_off = 0
    leds = ['red']
    update_leds(leds, blink_time_on, blink_time_off)

def yellow_constant():
    blink_time_on  = 0
    blink_time_off = 0
    leds = ['red', 'green']
    update_leds(leds, blink_time_on, blink_time_off)

def green_blink():
    blink_time_on  = 2.0
    blink_time_off = 0.5
    leds = ['green']
    update_leds(leds, blink_time_on, blink_time_off)

def red_blink():
    blink_time_on  = 1.0
    blink_time_off = 1.0
    leds = ['red']
    update_leds(leds, blink_time_on, blink_time_off)

def red_blink_fast():
    blink_time_on  = 0.5
    blink_time_off = 0.5
    leds = ['red']
    update_leds(leds, blink_time_on, blink_time_off)



def update_leds(current_leds, time_on, time_off):
    global led_pin
    global led_states
    global poll_interval

    if time_off == 0:
        # constant on
        for i in range(len(current_leds)):
            GPIO.output(led_pin[current_leds[i]], led_states['on'])
        time.sleep(poll_interval)
    else:
        # blink
        n_cycles = int(float(poll_interval) / float(time_on + time_off))
        for i in range(n_cycles):
            # led on, sleep, led off, sleep
            for i in range(len(current_leds)):
                GPIO.output(led_pin[current_leds[i]], led_states['on'])
            time.sleep(time_on)
            for i in range(len(current_leds)):
                GPIO.output(led_pin[current_leds[i]], led_states['off'])
            time.sleep(time_off)


# MAIN -------------------------------------------------

import time
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# If you are using a common Anode RGB LED use these - most RGB Leds are this type
led_states = {'off': GPIO.HIGH, 'on': GPIO.LOW}

# If you are using a common Cathode configuration use this instead
# led_states = {'off': GPIO.LOW, 'on': GPIO.HIGH}


# Specify the RasPi GPIO pins to use - modufy these to suit your configuration
led_pin = {'red': 21, 'green': 20}


# check the pi_power file every poll_interval seconds

poll_interval = 30

# Path to the .pi_power status file

pi_power_file_path = '/home/pi/.pi_power_status'

power_source = 'unknown'
power_fraction = 1.0

GPIO.setup(led_pin['red'],   GPIO.OUT)
GPIO.setup(led_pin['green'], GPIO.OUT)


# Read the .pi_power file at intervals and light the correct LED

while True:
    # read the .pi_power status file
    try:
        with open(pi_power_file_path, "r") as f:

            fields = f.read().rstrip().split(',')

            power_fraction = float(fields[0])
            power_source   = fields[1]
    except IOError:
        # dummy statement to handle python indentation...
        dummy = 1

    GPIO.output(led_pin['red'],   led_states['off'])
    GPIO.output(led_pin['green'], led_states['off'])

    if power_source == 'usb':
        green_blink()

    elif power_source == 'battery':

        # Modify the colors and cutoff levels to suit your needs

        if power_fraction >= 0.25:
            green_constant()
            # if you have an RGB LED try this instead
            # yellow_constant()

        elif power_fraction >= 0.15:
            red_constant()

        elif power_fraction >= 0.10:
            red_blink()

        else:
            red_blink_fast()
    else:
        # Leave LEDs off - just sleep
        time.sleep(poll_interval)
