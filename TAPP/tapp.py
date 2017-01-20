#!/usr/bin/env python

import argparse
import pymesh

def main():
	parser = argparse.ArgumentParser(description = 'TAPP Camera Pose Coverage Analysis')
	parser.add_argument('geotiff', action='store', type=str, help='GeoTIFF DEM for the search area')
	# Format should be XX.XXXXX, YY.YYYYY, northwestern corner first line, southwestern corner second line
	# TODO upgrade to ESRI shapefile in future
	parser.add_argument('search_area', action='store', type=str, help='Text file containing the northwestern and southwestern coordinates of the search area in decimal degrees, comma separated')
	# Format should be TAG: VALUE
	# Tags should be X_RES, Y_RES, X_FOV, Y_FOV
	parser.add_argument('camera_params', action='store', type=str, help='Text file containing the tagged camera parameters')
	# Format shoulc be a CSV file with the following columns with headers: LAT, LON, ALT, ROLL, PITCH, YAW
	# Yaw angle should be specified relative to true north
	parser.add_argument('poses', action='store', type=str, help='CSV file containing the camera poses')

	parser.parse_args()


if __name__ == '__main__':
	main()