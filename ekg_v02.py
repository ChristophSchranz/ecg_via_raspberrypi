#!\usr\bin\python
# -*- coding: utf-8 -*-

import time
import matplotlib.pyplot as plt

import RPi.GPIO as GPIO


# initialize the GPIOs (General Purpose Input and Output - Pins of the rpi)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# initialize MCP 3208 with its resolution and pins:

channel = 0  # measure voltage on pin 0

# MCP 3208 has a resolution of 12 bits, that means there are 2^12 states
# starting with state 0
resolution = 4095

# set pins to connect the MCP 3208 to the rpi
CLK = 11  # Clock
MISO = 9  # Master (rpi) in, Slave (MCP) out
MOSI = 10  # Master out, Slace in
CS = 8  # Chip Select (Master (rpi) can activate Slaves with this)

GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(CS, GPIO.OUT)

# set the sample rate (the amount measuremens per seconds) and measurement duration
sample_rate = 200
duration = 3


def read_adc(adcnum, clockpin = CLK, mosipin = MOSI, misopin = MISO, cspin = CS):
      '''returns channel in voltage'''
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
      for i in range(14):
              GPIO.output(clockpin, True)
              GPIO.output(clockpin, False)
              adcout <<= 1
              if (GPIO.input(misopin)):
                      adcout |= 0x1

      GPIO.output(cspin, True)
      
      adcout >>= 1       # first bit is 'null' so drop it
      return adcout # output in bitsdef


def measure_voltage(channel):
    ekg_data = list()  # make an empty list which will be appended
    time_stamps = list()
    
    for i in range(sample_rate*duration):
        # read_adc returns an integer between 0 and 2^12-1 = 4095
        # (0 means 0 V, 4095 means 5 V)
        # We need to scale this raw integer like this:
        voltage = -read_adc(channel) / resolution * 5

        # try to comment out theis print statement
        #print(voltage)

        # add every measurement to ekg_data with a time stamp
        ekg_data.append(voltage)
        time_stamps.append(time.time())
        
        time.sleep(1/sample_rate)


    print("Finished EKG measurement")
    
    plt.plot(time_stamps, ekg_data)
    
    plt.title("EKG Measurement")
    plt.xlabel("Time in Seconds")
    plt.ylabel("Voltage in Volt")
    
    plt.show()


if __name__ == "__main__":
    print("Starting EKG measurement")
    measure_voltage(channel)
