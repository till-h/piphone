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
		self.__timeout = timeout
		self.daemon = True
		self.start()

	def run(self):
		'''
		self.__rec_start.set()
		time.sleep(5)
		self.__rec_stop.set()
		'''
		GPIO.wait_for_edge(self.__start_pin, GPIO.FALLING)
		self.__rec_start.set()
		old_reading, new_reading = None, None
		while new_reading == old_reading:
			old_reading = GPIO.input(self.__stop_pin)
			time.sleep(0.01)
			new_reading = GPIO.input(self.__stop_pin)	
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
		#super(reader, self).__init__()
		self.__monitor = monitor
		self.__pins = pins
		self.__reading = {}
		self.__reading["time"] = []
		for p in self.__pins:
			self.__reading[str(p) + "_data"] = []
		#self.start()
	#def run(self):
		self.__monitor.wait_for_start()
		while not self.__monitor.stop():
			time.sleep(0.005)
			self.__reading["time"].append(time.time())
			for p in self.__pins:
				if GPIO.input(p):
					self.__reading[str(p) + "_data"].append(1)
				else:
					self.__reading[str(p) + "_data"].append(0)
	
	def get_readings(self):
		return self.__reading

class plotter(object):
	'''
	Top-level class to capture the dialpad operation at large.
	'''
	def __init__(self):
		# Set active pins
		GPIO.setmode(GPIO.BCM)
		self.__pins = [7, 8]
		self.__monitor = None
		self.__reader = None
		for p in self.__pins:
			GPIO.setup(p, GPIO.IN, pull_up_down = GPIO.PUD_UP)

	def record(self):
		self.__monitor = monitor(8, 8)
		self.__reader = reader(self.__monitor, self.__pins)

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

if __name__ == "__main__":
	print("plotter")
	plot = plotter()
	plot.record()
	print("plotting")
	plot.plot()

