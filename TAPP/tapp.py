#!/usr/bin/env python

import argparse
import pymesh
import Camera
import fileinput
import numpy as np

def read_meta_file(filename, tag):
	retval = None
	for line in fileinput.input(filename):
		if tag == line.strip().split(':')[0].strip():
			retval = line.strip().split(':')[1].strip()
			break
	fileinput.close()
	return retval

def main():
	parser = argparse.ArgumentParser(description = 'TAPP Camera Pose Coverage Analysis')
	parser.add_argument('geotiff', action='store', type=str, help='GeoTIFF DEM for the search area')
	# Format should be XX.XXXXX, YY.YYYYY, northwestern corner first line, southwestern corner second line
	# TODO upgrade to ESRI shapefile in future
	parser.add_argument('search_area', action='store', type=str, help='Text file containing the northwestern and southwestern coordinates of the search area in decimal degrees, comma separated')
	# Format should be TAG: VALUE
	# Tags should be X_RES, Y_RES, FOV, assuming square pixels!
	parser.add_argument('camera_params', action='store', type=str, help='Text file containing the tagged camera parameters')
	# Format should be a CSV file with the following columns with headers: LAT, LON, ALT, ROLL, PITCH, YAW
	# Yaw angle should be specified relative to true north
	# Altitude should be in meters AGL
	parser.add_argument('poses', action='store', type=str, help='CSV file containing the camera poses')

	args = parser.parse_args()

	geotiff_file = args.geotiff
	target_area_file = args.search_area
	camera_params = args.camera_params
	poses_file = args.poses

	# Load tiff to tiff->ply generator
	# TODO remove test
	ply_file = "../data/textured_plane.ply"

	# Load camera params
	x_res = float(read_meta_file(camera_params, "X_RES"))
	y_res = float(read_meta_file(camera_params, "Y_RES"))
	fov = float(read_meta_file(camera_params, "FOV"))
	camera = Camera(ply_file, x_res, y_res, fov)

	# Load camera poses
	poses = np.loadtxt(poses_file, delimiter=",", dtype={'names': ('LAT', 'LON', 'ALT', 'ROLL', 'PITCH', 'YAW'), 'formats': ('f8', 'f8', 'f8', 'f8', 'f8', 'f8')}, skiprows=1)
	# Transform pose to local frame!

	for pose in poses:
		camera.snap(pose)


if __name__ == '__main__':
	main()