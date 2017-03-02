#!/usr/bin/env python

import serial
import pymavlink

def main():
	port = serial.Serial("/dev/ttyUSB0", baudrate = 115200, timeout = 3.0)
	while True:
		line = port.readline()
		if len(line.split()) != 4:
			continue
		alt = float(line.split()[0])
		if alt == 130.00:
			print("noval")
		else:
			print(alt)


if __name__ == '__main__':
	main()