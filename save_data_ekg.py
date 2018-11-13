#!\usr\bin\python3
# -*- coding: utf-8 -*-

import time  # import the module called "time"
import matplotlib.pyplot as plt  # import the grafic-module as plt

import RPi.GPIO as GPIO  # import the GPIO to use the Pins


# set the sample rate (number of measurements per seconds) and its duration
sample_rate = 200
duration = 20

# initialize MCP 3208 with its resolution and pins:
channel = 0  # measure voltage on pin 0

# MCP 3208 has a resolution of 12 bits, that means there are 2^12 states
# starting with state 0
resolution = 4095

# set pins to connect the MCP 3208 to the rpi
CLK = 11  # Clock
MISO = 9  # Master (rpi) in, Slave (MCP) out
MOSI = 10  # Master out, Slace in
CS = 7  # Chip Select (Master (rpi) can activate Slaves with this)

# initialize the GPIOs (General Purpose Input and Output)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# set the pins as output or input
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(MOSI, GPIO.OUT)
GPIO.setup(MISO, GPIO.IN)
GPIO.setup(CS, GPIO.OUT)


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
    # create empty lists which will be appended
    ekg_data = list()  
    time_stamps = list()

    # This is a for loop. The code intended below a for loop will be excuted
    # sample_rate*duration times.
    for i in range(sample_rate*duration):
        # read_adc returns an integer between 0 and 2^12-1 = 4095
        # (0 means 0 V, 4095 means 5 V)
        # We need to scale this raw integer like this:
        voltage = read_adc(channel) / resolution * 5

        # TODO: try to comment out this print statement
        #print(voltage)

        # add each data point the lists
        ekg_data.append(voltage)
        time_stamps.append(time.time())

        # wait 1/sample_rate seconds
        time.sleep(1/sample_rate)


    print("Finished EKG measurement")
    filename = str(time.time())
    with open("data/{}".format(filename), "a") as f:
        for i, line in enumerate(ekg_data):
              f.write("\n"+str(time_stamps[i])+", "+str(line))

    # This routine plots (creates a grafic) the data
    plt.plot(time_stamps, ekg_data)
    
    plt.title("EKG Measurement")
    plt.xlabel("Time in Seconds")
    plt.ylabel("Voltage in Volt")
    
    plt.show()


# The code will be started from this point on.
if __name__ == "__main__":
    print("Starting EKG measurement")
    # The function measure_voltage will be executed (called) with the argument
    # "channel" which was defined on at the top of the code.
    measure_voltage(channel)
