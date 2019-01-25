#!/usr/bin/env python
import time
import matplotlib
import matplotlib.pyplot as plt
import RPi.GPIO as GPIO
import threading
import numpy

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
		self.__reading = {}
		self.__reading["time"] = []
		for p in self.__pins:
			self.__reading[str(p) + "_data"] = []

	def start(self):
		self.__monitor.wait_for_start()
		while not self.__monitor.stop():
			time.sleep(0.005)
			self.__reading["time"].append(time.time())
			for p in self.__pins:
				if GPIO.input(p):
					self.__reading[str(p) + "_data"].append(1)
				else:
					self.__reading[str(p) + "_data"].append(0)
	
	def get_reading(self):
		return self.__reading

class plotter(object):
	'''
	Top-level class to capture the dialpad operation at large.
	'''
	def __init__(self):
		# Set active pins
		GPIO.setmode(GPIO.BCM)
		self.__monitor = monitor(8, 8)
		self.__reader = reader(self.__monitor, [7, 8])

	def record(self):
		self.__reader.start()

	def plot(self):
		plt.figure()
		readings = self.__reader.get_reading()
		for key in (key for key in readings if key.find("_data") > 0):
			plt.plot(numpy.array(readings["time"]) - readings["time"][0], readings[key], label = key.replace("_data",""))
		plt.legend()
		plt.show(block = False)
		raw_input()
		plot.close("all")
	
	def get_reading(self):
		return self.__reader.get_reading()

	def close(self, param):
		plt.close(param)

if __name__ == "__main__":
	plot = plotter()
	print("Plotter. Please dial a number.")
	plot.record()
	print("Plotting...")
	print plot.get_reading()
	plot.plot()

