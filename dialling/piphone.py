#! /usr/bin/python
  2 
  3 import RPi.GPIO as GPIO
  4 import datetime
  5 from __future__ import print_function
  6 import matplotlib as mpl
  7 
  8 matplotlib.use("GTK")
  9 
 10 def notify_rising(channel):
 11         print("{} RISE".format(channel))
 12 
 13 def notify_falling(channel):
 14         print("{} FALL".format(channel))
 15 
 16 class dialpad:
 17         def __init__(self):
 18                 # Set active pins 
 19                 self.__pins = [7, 8]
 20                 GPIO.cleanup()
 21                 GPIO.setmode(GPIO.BCM)
 22                 reading = {}
 23                 reading["time"] = []
 24                 for p in self.__pins: 
 25                         GPIO.setup(p, GPIO.IN, pull_up_down = GPIO.PUD_UP)
 26                         reading[str(p) + "_data"] = []
 27         
 28         def __del__(self):
 29                 GPIO.cleanup()
 30         
 31         def test(self):
 32                 for i in range(3000):
 33                         for p in self.__pins:
 34                                 if GPIO.input(p):
 35                                         reading[str(p) + "_data"] = 1
 36                                 else:   
 37                                         reading[str(p) + "_data"] = 0
 38                         reading["time"] = datetime.datetime.time(datetime.datetime.now())
 39                 mpl.figure()
 40                 mpl
 41                 
 42         def dial(self):
 43                 number = ""
 44                 return number
 45 
 46 if __name__ == "__main__":
 47         dialpad = dialpad()
 48         input("Press key to start recording")
 49         dialpad.test()

