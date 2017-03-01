#!/usr/bin/env python

from pymavlink import mavutil
import mavlink

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

if __name__ == '__main__':
	mav_master = mavutil.mavlink_connection('127.0.0.1:14550', 115200)
	mav_master.wait_heartbeat()
	waypoints = getWaypoints(mav_master)
	mav_master.set_mode(mav_master.mode_mapping()['GUIDED'])	
	msg = mav_master.recv_match(blocking=True, timeout=10, type='COMMAND_ACK')
	if msg.result != 0:
		print("Failed to set mode!")
	mav_master.arducopter_arm()
	msg = mav_master.recv_match(blocking=True, timeout=10, type='COMMAND_ACK')
	if msg.result != 0:
		print("Failed to arm!")
		# Failed to arm!
		
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
	msg = mav_master.recv_match(blocking=True, timeout=20, type='MISSION_ITEM_REACHED')

	while True:
		msg = mav_master.recv_match(blocking=True, timeout=10)
		print(msg.get_type())
		if msg.get_type() ==  'MISSION_CURRENT':
			if waypoints[msg.seq].command == mavlink.MAV_CMD_NAV_WAYPOINT:
				target_altitude = waypoints[msg.seq].z
				# print(target_altitude)
				# mav_master.mav.command_long_send(mav_master.target_system, mav_master.target_component,mavlink.MAV_CMD_DO_CHANGE_SPEED, 0, 0,3,0,0,0,0,0,0)
				# mav_master.mav.command_long_send(mav_master.target_system, mav_master.target_component, mavlink.MAV_CMD_CONDITION_CHANGE_ALT, 0, -2,0,0,0,0,0,20)
				# msg = mav_master.recv_match(blocking=True, timeout=10, type='COMMAND_ACK')
				# if msg.result != 0:
					# print("Failed to set alt!")
		elif msg.get_type() == 'HEARTBEAT':
			if msg.base_mode & 0x80 == 0:
				print("Landed")
				break

