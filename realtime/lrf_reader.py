#!/usr/bin/env python

import serial
import pymavlink
import time

def main():
	port = serial.Serial("/dev/ttyUSB0", baudrate = 115200, timeout = 3.0)
	start = time.time()
	count = 0;
	while count < 100:
		line = port.readline()
		if len(line.split()) != 4:
			continue
		alt = float(line.split()[0])
		# if alt == 130.00:
		# 	print("noval")
		# else:
		# 	print(alt)
		count = count + 1
	end = time.time()
	tdelta = end - start
	print(100.0 / tdelta)


if __name__ == '__main__':
	main()