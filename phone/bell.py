#!/usr/bin/env python

from time import sleep
from gpiozero import OutputDevice

f = 1 # Hz

half_period = 1 / f / 2

a_enable = OutputDevice(16)
a_1 = OutputDevice(20)
a_2 = OutputDevice(21)
a_enable.on()

#led = OutputDevice(14)
#led.on()
#sleep(2)

if __name__ == "__main__":
	try:
		while True:
			a_1.on()
			a_2.off()
			sleep(half_period)		
			a_1.off()
			a_2.on()
			sleep(half_period)
	except KeyboardInterrupt:
		print("Quit")
		a_enable.off()

