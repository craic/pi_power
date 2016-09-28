#!/usr/bin/env python

# pi_power.py

# Robert Jones 2016 jones@craic.com

# The code for reading the MCP3008 analog to digital convertor (readadc) was
# written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain


# Works with an Adafruit PowerBoost 1000C LiPo battery charger

# Writes the fraction of battery remaining as well as the current power source to the file /home/pi/.pi_power

# format:  <float 0.00 - 1.00>,<string [battery|usb]>
# 0.75,battery
# 1.00,usb



import time
import os
import argparse
import RPi.GPIO as GPIO


# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout


# Calculate the output of a voltage divider
# voltage_divider layout is:
# Vin ---[ R1 ]---[ R2 ]---GND
#               |
#              Vout
#
# Vout = R2 / (R1 + R2) * Vin
# e.g. if R1 = 6800 and R2 = 10000 and Vin is 5.2V then Vout is 3.095
#
def voltage_divider(r1, r2, vin):
        vout = vin * (r2 / (r1 + r2))
        return vout



# Set up a trigger to shutdown the system when the power button is pressed
# define a setup routine and the actual shutdown method

# The shutdown code is based on that in https://github.com/NeonHorizon/lipopi

def user_shutdown_setup(shutdown_pin):
    # setup the pin to check the shutdown switch - use the internal pull down resistor
    GPIO.setup(shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    # create a trigger for the shutdown switch
    GPIO.add_event_detect(shutdown_pin, GPIO.RISING, callback=user_shutdown, bouncetime=1000)

# User has pressed shutdown button - initiate a clean shutdown
def user_shutdown(channel):
    global safe_mode
        
    shutdown_delay = 10 # seconds

    # in Safe Mode, wait 2 mins before actually shutting down
    if(safe_mode):
        cmd = "sudo wall 'System shutting down in 2 minutes - SAFE MODE'"
        os.system(cmd)
        time.sleep(120)

    cmd = "sudo wall 'System shutting down in %d seconds'" % shutdown_delay
    os.system(cmd)
    time.sleep(shutdown_delay)

    # Log message is added to /var/log/messages
    os.system("sudo logger -t 'pi_power' '** User initiated shut down **'")
    GPIO.cleanup()
    os.system("sudo shutdown now")


# Shutdown system because of low battery
def low_battery_shutdown():
    global safe_mode

    shutdown_delay = 30 # seconds
    
    # in Safe Mode, wait 2 mins before actually shutting down
    if(safe_mode):
        cmd = "sudo wall 'System shutting down in 2 minutes - SAFE MODE'"
        os.system(cmd)
        time.sleep(120)
    
    cmd = "sudo wall 'System shutting down in %d seconds'" % shutdown_delay
    os.system(cmd)
    time.sleep(shutdown_delay)
    # Log message is added to /var/log/messages
    os.system("sudo logger -t 'pi_power' '** Low Battery - shutting down now **'")
    GPIO.cleanup()
    os.system("sudo shutdown now")
                

    

# MAIN -----------------------

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Command Line Arguments
# --log    write time, voltage, etc to a log file
# --debug  write time, voltage, etc to STDOUT

parser = argparse.ArgumentParser(description='Pi Power - Monitor battery status on RasPi projects powered via Adafruit PowerBoost 1000C')

parser.add_argument('-d', '--debug', action='store_true')
parser.add_argument('-l', '--log',   action='store_true')
parser.add_argument('-s', '--safe',  action='store_true')

args = parser.parse_args()

safe_mode = False
if(args.safe):
        safe_mode = True

        
# Setup the GPIO pin to use with the use shutdown button

user_shutdown_pin = 26
user_shutdown_setup(user_shutdown_pin)


# Setup the connection to the ADC

# specify the Raspberry Pi GPIO pins to be used to connect to the SPI interface on the MCP3008 ADC

SPICLK  = 18
SPIMISO = 23
SPIMOSI = 24
SPICS   = 25

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK,  GPIO.OUT)
GPIO.setup(SPICS,   GPIO.OUT)

# Vbat to adc #0, Vusb connected to #1
v_bat_adc_pin = 0
v_usb_adc_pin = 1

# Voltage divider drops the PowerBoost voltage from around 5V to under 3.3V which is the limit for the Pi
voltage_divider_r1 =  6800.0
voltage_divider_r2 = 10000.0

# Define the min and max voltage ranges for the inputs

usb_min_voltage = 0.0
usb_max_voltage = 5.2

gpio_min_voltage = 0.0
gpio_max_voltage = 3.3

# LiPo battery voltage range - actual range is 3.7V to 4.2V
# But in practice the measured range is reduced as Vbat always drops from 4.2 to around 4.05 when the
# USB cable is removed - so this is the effective range:

battery_min_voltage = 3.75
battery_max_voltage = 4.05

# this is the effective max voltage, prior to the divider, that the ADC can register
adc_conversion_factor = (gpio_max_voltage / voltage_divider(voltage_divider_r1, voltage_divider_r2, usb_max_voltage)) * usb_max_voltage


pi_power_status_path = '/home/pi/.pi_power_status'
pi_power_log_path    = '/home/pi/pi_power_log.csv'


# initialize an empty log file
if(args.log):
        with open(pi_power_log_path, "w") as f:
                f.write('Time,Vbat,Vusb,Frac,Source\n')


# Take a measurement every poll_interval * seconds * - default 60
poll_interval = 60

power_source = ''
power_source_previous = ''

fraction_battery = 1.0

# Define the minimum battery level at which shutdown is triggered

fraction_battery_min = 0.075


if(args.debug):
        print 'Time    Vbat   Vusb   Frac   Source'


elapsed_time = 0
msg = ''

while True:
        # read the analog pins on the ACD (range 0-1023) and convert to 0.0-1.0
        frac_v_bat = round(readadc(v_bat_adc_pin,   SPICLK, SPIMOSI, SPIMISO, SPICS)) / 1023.0
        frac_v_usb = round(readadc(v_usb_adc_pin,   SPICLK, SPIMOSI, SPIMISO, SPICS)) / 1023.0
       
        # Calculate the true voltage
        v_bat = frac_v_bat * adc_conversion_factor
        v_usb = frac_v_usb * adc_conversion_factor
                       

        fraction_battery = (v_bat - battery_min_voltage) / (battery_max_voltage - battery_min_voltage)

        if fraction_battery > 1.0:
               fraction_battery = 1.0
        elif fraction_battery < 0.0:
               fraction_battery = 0.0

        
        # is the USB cable connected ? Vusb is either 0.0 or around 5.2V       
        if v_usb > 1.0:
                power_source = 'usb'
        else:
                power_source = 'battery'

        if power_source == 'usb' and power_source_previous == 'battery':
                print '** USB cable connected'
        elif power_source == 'battery' and power_source_previous == 'usb':
                print '** USB cable disconnected'

        power_source_previous = power_source

        msg = ''
        # If battery is too low then shutdown
        if fraction_battery < fraction_battery_min:
               msg = 'Low Battery - shutdown now'
               if(args.debug):
                       print "** LOW BATTERY - shutting down........"
               # shutdown after writing to the log file

        if(args.debug):
                print '{0:6d}  {1:.3f}  {2:.3f}  {3:.3f}  {4:s}  {5:s}'.format(elapsed_time, v_bat, v_usb, fraction_battery, power_source, msg)

        # Open log file, write one line and close
        # This handles the case where the battery is allowed to drain completely and 
        # shutdown in which case the file may be corrupted
        if(args.log):
                with open(pi_power_log_path, "a") as f:
                        f.write('{0:d},{1:.3f},{2:.3f},{3:.3f},{4:s},{5:s}\n'.format(elapsed_time, v_bat, v_usb, fraction_battery, power_source, msg))

        # Write the .pi_power status file - used by pi_power_leds.py
        with open(pi_power_status_path, "w") as f:
                f.write('{0:.3f},{1:s}\n'.format(fraction_battery,power_source))

        # Low battery shutdown - specify the time delay in seconds
        if fraction_battery < fraction_battery_min:
                low_battery_shutdown()
        
        # sleep poll_interval seconds between updates
        time.sleep(poll_interval)

        elapsed_time += poll_interval


