#! /usr/bin/env python

from __future__ import print_function
import RPi.GPIO as GPIO
import datetime
import time

def notify_rising(channel):
	print("{} RISE".format(channel))

def notify_falling(channel):
	print("{} FALL".format(channel))

class dialpad:
	def __init__(self):
		# Set active pins
		self.__pins = [7, 8]
		GPIO.cleanup()
		GPIO.setmode(GPIO.BCM)
		self.reading = {}
		self.reading["time"] = []
		for p in self.__pins:
			GPIO.setup(p, GPIO.IN, pull_up_down = GPIO.PUD_UP)
			self.reading[str(p) + "_data"] = []

	def __del__(self):
		GPIO.cleanup()

	def test(self):
		for i in range(3000):
			for p in self.__pins:
				if GPIO.input(p):
					self.reading[str(p) + "_data"].append(1)
				else:
					self.reading[str(p) + "_data"].append(0)
			self.reading["time"].append(datetime.datetime.time(datetime.datetime.now()))
			time.sleep(0.001)

	def dial(self):
		number = ""
		return number

	def get_reading(self):
		return self.reading

if __name__ == "__main__":
	dialpad = dialpad()
	time.sleep(2)
	print("START")
	dialpad.test()
	print("{}".format(str(dialpad.get_reading())))
	print("END")
