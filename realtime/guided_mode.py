#!/usr/bin/env python

from pymavlink import mavutil
import mavlink
import utm
import numpy as np
from threading import Thread
import serial
# import picamera
import os
from pexif import JpegFile

alt = 0
img_num = 0
TARGET_ALT = 30
OUTPUT_DIR = './'

def do_setup_camera():
	global camera
	camera = picamera.PiCamera()

def do_trigger_camera(arg):
	global img_num
	global OUTPUT_DIR
	image_name = os.path.join(OUTPUT_DIR, '%s_%d.jpg' % ('img', img_num))
	print(image_name)
	# camera.capture(image_name)
	# ef = JpegFile.fromFile(image_name)
	# ef.set_geo(arg[0], arg[1])
	# ef.writeFile(image_name)
	img_num = img_num + 1


def lrf_thread(arg):
	port = serial.Serial(arg, baudrate = 115200, timeout = 3.0)
	global alt
	while True:
		line = port.readline()
		alt = float(line.split()[0])
		alt = 30 # for testing

def getWaypoints(mav_master):
	mav_master.waypoint_request_list_send()
	msg = mav_master.recv_match(blocking=True, timeout=10, type='MISSION_COUNT')
	waypoints = []
	for i in xrange(msg.count):
		mav_master.waypoint_request_send(i)
		waypoint_msg = mav_master.recv_match(blocking=True, timeout=10, type='MISSION_ITEM')
		waypoints.append(waypoint_msg)
	return waypoints

def getTakeoff(waypoints):
	for i in xrange(1, len(waypoints)):
		if waypoints[i].command == mavlink.MAV_CMD_NAV_TAKEOFF:
			return waypoints[i]

def getTakeoffIdx(waypoints):
	for i in xrange(1, len(waypoints)):
		if waypoints[i].command == mavlink.MAV_CMD_NAV_TAKEOFF:
			return i


if __name__ == '__main__':
	targs = '/dev/ttyUSB0'
	t = Thread(target=lrf_thread, args = {targs})
	t.daemon = True
	t.start()

	# do_setup_camera()

	mav_master = mavutil.mavlink_connection('127.0.0.1:14550', 115200)
	mav_master.wait_heartbeat()
	mav_master.wait_gps_fix()
	waypoints = getWaypoints(mav_master)

	msg = mav_master.recv_match(blocking=True, type='HEARTBEAT', timeout = 10)
	if msg.base_mode & 0x80 != 0:
		print("Not Disarmed!")
		exit()

	mav_master.set_mode(mav_master.mode_mapping()['GUIDED'])	
	msg = mav_master.recv_match(blocking=True, timeout=10, type='COMMAND_ACK')
	if msg.result != 0:
		print("Failed to set mode!")
	else:
		print("Mode set to GUIDED")
	mav_master.arducopter_arm()
	msg = mav_master.recv_match(blocking=True, timeout=10, type='COMMAND_ACK')
	if msg.result != 0:
		print("Failed to arm!")
		# Failed to arm!
	else:
		print("Copter armed")
		
	takeoffwpt = getTakeoff(waypoints)
	mav_master.mav.command_long_send(
		mav_master.target_system,
		mavlink.MAV_COMP_ID_SYSTEM_CONTROL,
		mavlink.MAV_CMD_NAV_TAKEOFF,
		0, # confirmation
		0, # param1
		0, # param2
		0, # param3
		0, # param4
		0, # param5
		0, # param6
		takeoffwpt.z) # param7)
	msg = mav_master.recv_match(blocking=True, timeout=10, type='COMMAND_ACK')
	if msg.result != 0:
		print("Failed to takeoff!")
		exit()
		# Failed to arm!
	mav_master.recv_match(blocking=True, timeout=20, type='MISSION_ITEM_REACHED')
	print("Takeoff complete")

	msg = mav_master.recv_match(blocking=True, timeout=10, type='GLOBAL_POSITION_INT')

	currentLat = msg.lat / 1e7
	currentLon = msg.lon / 1e7
	currentAlt = msg.relative_alt / 1e3

	currentUTM = utm.from_latlon(currentLat, currentLon)
	camera_trigger_distance = -1
	travelledDistance = 0
	numTriggers = 0

	for i in xrange(getTakeoffIdx(waypoints), len(waypoints)):
		if waypoints[i].command == mavlink.MAV_CMD_DO_SET_CAM_TRIGG_DIST:
			camera_trigger_distance = waypoints[i].param1
			travelledDistance = 0
			numTriggers = 0
			print(camera_trigger_distance)
		if waypoints[i].command != mavlink.MAV_CMD_NAV_WAYPOINT:
			continue
		targetUTM = utm.from_latlon(waypoints[i].x, waypoints[i].y)
		
		msg = mav_master.recv_match(blocking = True, timeout=1, type = 'GLOBAL_POSITION_INT')
		print("Sending position target")
		bitmask = 0xffff & ~(1 << 1) & ~(1 << 2) & ~(1 << 3)
		mav_master.mav.set_position_target_global_int_send(
			msg.time_boot_ms,
			mav_master.target_system,
			mav_master.target_component,
			mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
			0b0000111111111000,
			int(waypoints[i].x * 1e7),
			int(waypoints[i].y * 1e7),
			int(waypoints[i].z),
			5, # vx
			0, # vy
			targetVelocity, # vz
			2, # afx
			2, # afy
			2, # afz
			0, # yaw
			0) # yaw_rate

		currentUTM = utm.from_latlon(msg.lat / 1e7, msg.lon / 1e7)
		prevLocation = currentUTM[0] + 1j * currentUTM[1]

		while True:
			msg = mav_master.recv_match(blocking = True, timeout = 2, type = 'GLOBAL_POSITION_INT')
			if msg is None:
				exit()
			currentUTM = utm.from_latlon(msg.lat / 1e7, msg.lon / 1e7)
			currentLocation = currentUTM[0] + 1j * currentUTM[1]
			targetVector = targetUTM[0] - currentUTM[0] + 1j * (targetUTM[1] - currentUTM[1])
			distanceFromTarget = np.abs(targetVector)
			velocityVector = targetVector / distanceFromTarget * 5
			currentALt = msg.relative_alt
			if alt > TARGET_ALT:
				targetVelocity = -5
			else:
				targetVelocity = 5
			if distanceFromTarget < 5:
				print("Waypoint reached")
				break;
			else:
				targetAltitude = waypoints[i].z
				mav_master.mav.set_position_target_global_int_send(
					msg.time_boot_ms,
					mav_master.target_system,
					mav_master.target_component,
					mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT,
					0b0000111111111000,
					int(waypoints[i].x * 1e7),
					int(waypoints[i].y * 1e7),
					int(currentAlt - (alt - TARGET_ALT)),
					5, # vx
					0, # vy
					targetVelocity, # vz
					2, # afx
					2, # afy
					2, # afz
					0, # yaw
					0) # yaw_rate
			if camera_trigger_distance > 0:
				travelledDistance = travelledDistance + (np.abs(currentLocation - prevLocation))
				if int(travelledDistance / camera_trigger_distance) > numTriggers:
					do_trigger_camera({msg.lat, msg.lon})
					numTriggers = numTriggers + 1
			prevLocation = currentLocation

	mav_master.set_mode(mav_master.mode_mapping()['RTL'])	
	msg = mav_master.recv_match(blocking=True, timeout=10, type='COMMAND_ACK')
	if msg.result != 0:
		print("Failed to set mode!")
	else:
		print("Mode set to RTL")

	while True:
		msg = mav_master.recv_match(blocking=True, timeout=10)
		if msg.get_type() == 'HEARTBEAT':
			if msg.base_mode & 0x80 == 0:
				print("Landed")
				break

