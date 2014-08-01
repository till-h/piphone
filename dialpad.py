#!/usr/bin/env python
import time
import matplotlib
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import threading
import numpy
import logging # TODO do proper logging

class monitor(threading.Thread):
	'''
	Class to monitor the dialpad and signal when to start and when to stop recording.
	'''
	def __init__(self, start_pin, stop_pin, timeout = 1):
		super(monitor, self).__init__()
		self.__rec_start = threading.Event()
		self.__rec_stop  = threading.Event()
		self.__start_pin = start_pin
		self.__stop_pin = stop_pin
		self.daemon = True
		self.start()

	def run(self):
		GPIO.wait_for_edge(self.__start_pin, GPIO.BOTH)
		self.__rec_start.set()
		GPIO.wait_for_edge(self.__stop_pin, GPIO.BOTH)
		self.__rec_stop.set()

	def wait_for_start(self):
		'''
		Blocks until start event is set.
		'''
		self.__rec_start.wait()
			
	def stop(self):
		'''
		Returns True if recording can be finished.
		'''
		return self.__rec_stop.isSet()


class reader(object):
	'''
	Class to read out and save pin potentials.
	'''
	def __init__(self, monitor, pins):
		self.__monitor = monitor
		self.__pins = pins
		for p in self.__pins:
			GPIO.setup(p, GPIO.IN, pull_up_down = GPIO.PUD_UP)
		self.reset()

	def reset(self):
		self.__reading = {}
		self.__reading["time"] = []
		for p in self.__pins:
			self.__reading[str(p) + "_data"] = []

	def read_one_number(self):
		self.__monitor.wait_for_start()
		while not self.__monitor.stop():
			time.sleep(0.005)
			self.__reading["time"].append(time.time())
			for p in self.__pins:
				if GPIO.input(p):
					self.__reading[str(p) + "_data"].append(1)
				else:
					self.__reading[str(p) + "_data"].append(0)
	
	def get_reading(self, pin = None):
		if pin == None:
			return self.__reading
		else:
			return self.__reading[str(pin) + "_data"]
class dialpad(object):
	'''
	Top-level class to capture the dialpad operation at large.
	'''
	def __init__(self):
		# Set active pins
		GPIO.setmode(GPIO.BCM)
		self.__monitor = monitor(8, 8)
		self.__reader = reader(self.__monitor, [7, 8])
		self.__analyser = crosscorrelation_analyser()

	def dial_one_number(self):
		self.__reader.read_one_number()
		return self.__analyser.analyse(self.__reader.get_reading(7))

	def plot(self):
		plt.figure()
		readings = self.__reader.get_readings()
		for key in (key for key in readings if key.find("_data") > 0):
			plt.plot(numpy.array(readings["time"]) - readings["time"][0], readings[key], label = key.replace("_data",""))
		plt.legend()
		plt.show(block = False)
		raw_input()
		plot.close("all")

	def close(self, param):
		plt.close(param)

class crosscorrelation_analyser(object):
	'''
	Analyse the reading coming from the dialpad (reader class)
	to determine which number was dialled.
	'''
	def __init__(self, one_pulse = None):
		if one_pulse == None:
			self.__one_pulse = [0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0]
		self.__autocorrelation_max = max(numpy.correlate(self.__one_pulse, self.__one_pulse, mode = 'valid'))

	def analyse(self, reading):
		try:
			truncation_idx = numpy.nonzero(numpy.diff(reading))[0][0]
		except IndexError:
			return None
		reading = reading[truncation_idx:]
		crosscorrelation = numpy.correlate(reading, self.__one_pulse, mode='valid')
		plt.figure()
		plt.plot(crosscorrelation)
		plt.show(block = True)
		crosscorrelation.sort()
		return digit
		
	

if __name__ == "__main__":
	dialpad = dialpad()
	print("Please dial a number.")
	print dialpad.dial_one_number()
	print("Plotting...")

