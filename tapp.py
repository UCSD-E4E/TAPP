#!/usr/bin/env python3

import sys
import os

import argparse
import fileinput
import numpy as np
from osgeo import gdal

from TAPP.Camera import Camera
from utils import gdal_utils


def read_meta_file(filename, tag):
    """Reads a tag from a metadata file

        Args:
            filename (string):  Metadata filepath
            tag (string):       Tag to read

        Return:
            value (string): The first value referenced by the tag
    """

    retval = None
    for line in fileinput.input(filename):
        if tag == line.strip().split(':')[0].strip():
            retval = line.strip().split(':')[1].strip()
            break
    fileinput.close()
    return retval


def main():
    """Main script logic"""
    parser = argparse.ArgumentParser(description='TAPP Camera Pose Coverage'
                                     'Analysis')

    parser.add_argument('geotiff', action='store', type=str,
                        help='GeoTIFF DEM for the search area')

    # Format should be XX.XXXXX, YY.YYYYY, northwestern corner first line,
    #   southwestern corner second line
    # TODO upgrade to ESRI shapefile in future
    parser.add_argument('search_area', action='store', type=str,
                        help='Text file containing the northwestern and '
                        'southwestern coordinates of the search area in'
                        ' decimal degrees, comma separated')

    # Format should be TAG: VALUE
    # Tags should be X_RES, Y_RES, FOV, assuming square pixels!
    parser.add_argument('camera_params', action='store', type=str,
                        help='Text file containing the tagged camera '
                        'parameters')

    # Format should be a CSV file with the following columns with headers:
    #   LAT, LON, ALT, ROLL, PITCH, YAW
    # Yaw angle should be specified relative to true north
    # Altitude should be in meters AGL
    parser.add_argument('poses', action='store', type=str,
                        help='CSV file containing the camera poses')

    args = parser.parse_args()

    geotiff_file = args.geotiff
    target_area_file = args.search_area
    camera_params = args.camera_params
    poses_file = args.poses

    # Trim tiff
    print("Trimming tiff")
    target_area = np.genfromtxt(target_area_file, delimiter=',')
    retval = gdal_utils.trim(target_area[0], target_area[1],
                             geotiff_file, 'tmp.tiff')

    # Load tiff to tiff->ply generator
    print("Tiff -> Mesh")
    retval = gdal_utils.tif2mesh('tmp.tiff', 'tmp.ply', 1, 0)
    ply_file = 'tmp.ply'

    # Load camera params
    print("Loading camera params")
    x_res = float(read_meta_file(camera_params, "X_RES"))
    y_res = float(read_meta_file(camera_params, "Y_RES"))
    fov = float(read_meta_file(camera_params, "FOV"))
    camera = Camera(ply_file, x_res, y_res, fov, 0)

    # Load camera poses
    print("Loading camera poses")

    # Setup dtype
    params = ('EASTING', 'NORTHING', 'ALT', 'ROLL', 'PITCH', 'YAW')
    formats = ('f8', 'f8', 'f8', 'f8', 'f8', 'f8')

    poses = np.loadtxt(poses_file, delimiter=",", dtype={'names': params,
                       'formats': formats}, skiprows=1)

    # Transform pose to local frame!
    tif = gdal.Open(geotiff_file)
    tf = tif.GetGeoTransform()

    print("Processing poses")
    for pose in poses:
        px, py = gdal_utils.coord2pixel(tf, pose['EASTING'], pose['NORTHING'])

        print("Pixel X: %f, Pixel Y: %f, Alt: %f, Roll %f, Pitch %f, Yaw %f" %
              (px, py, pose['ALT'], pose['ROLL'], pose['PITCH'], pose['YAW']))

        camera.snap(pose)

    print("Finished processing")
    camera.closePly()


if __name__ == '__main__':
    main()
