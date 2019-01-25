#!/bin/env python
import sys
import multiprocessing as mp
from readchar import readkey


class Simulator():
    
    def __init__(self):
        self.q = mp.Queue()
    
    def printer(self, queue):
        while True:
            if not self.q.empty():
                key = self.q.get(True, .25)
                print('Printer. Received {}'.format(key))
                sys.stdout.flush()

    def run(self):
        printer = mp.Process(target=self.printer, args=(self.q,))
        printer.start()
        while True:
            key = readkey()
            if key == 'q':
                print('Exit')
                printer.terminate()
                return
            print('Main. Pressed {}'.format(key))
            self.q.put(key)

if __name__ == '__main__':
    print(mp.cpu_count())
    s = Simulator()
    s.run()
