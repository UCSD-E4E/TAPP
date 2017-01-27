from plyfile import PlyData, PlyElement
from osgeo import gdal

import subprocess
import numpy as np
import scipy.ndimage


def pixel2coord(tf, x, y):
    """Returns global coordinates from pixel x, y coordinates"""
    lat = tf[0] + x*tf[1] + y*tf[2]
    lon = tf[3] + x*tf[4] + y*tf[5]

    return lat, lon


def coord2pixel(tf, lat, lon):
    """Transforms lat/lon coordinates to pixel coordinates"""
    x = int(round((lat-tf[0])/tf[1]))
    y = int(round((lon-tf[3])/tf[5]))

    return x, y


def trim(lat1, lon1, lat2, lon2, infile, outfile):
    '''
    Calls gdal_translate using the provided arguments to trim a larger tif
    file into a smaller one based on the upper left and lower right lat/lon
    pairs.

        Args:
            lat1, lon1 (float): Upper left corner lat/lon

            lat2, lon2 (float): Lower right corner lat/lon

        Return:
            returncode (int): Return code from calling gdal_translate

    '''
    transform = gdal.Open(infile).GetGeoTransform()

    x1, y1 = coord2pixel(transform, lat1, lon1)
    x2, y2 = coord2pixel(transform, lat2, lon2)

    args = ['gdal_translate', '-srcwin']
    args.extend([str(x1), str(y1), str(x2-x1), str(y2-y1), infile, outfile])

    try:
        res = subprocess.check_output(args, stderr=subprocess.STDOUT)
    except Exception as ex:
        res = ex.returncode, str(ex.output)

    return res


def tif2mesh(tiffile, plyfile, upsample, interpolation):
    """
    Turns a tif file into a ply mesh file. Note that for the scale to be
    correct we assume that the tiff file is in meters. This is handled
    correctly for utm formats where the pixel size is given in meters.

    Args:
        tiffile (string): File name of the tif we are converting

        plyfile (string): Outputfile name

        upsample (int): The magnitude which to upsample the grid, i.e. a
            sample rate of 2 will effectively square the size image.

        interpolation (int): The method by which to interpolate points if we
            are upsampling. (0 = Nearest, 1 = Bilinear, 3 = Cubic). Nominally
            there are 5 different orders but I can't find the documentation on
            what they are.

    Return:
        size: (numpy.shape) The effective grid size after the transformation

    """
    tif = gdal.Open(tiffile)
    tf = tif.GetGeoTransform()

    faces = []
    cnt = 0

    # Get image x,y,z
    channel = tif.GetRasterBand(1)
    no_value = channel.GetNoDataValue()

    # channel = np.array(tif.GetRasterBand(1).ReadAsArray()).astype(np.float32)
    channel = np.array(channel.ReadAsArray().astype(np.float32))

    # Upsample the image with cubic interpolation
    channel = scipy.ndimage.zoom(channel, upsample, order=interpolation)

    # Create our point cloud with excessive use of list comprehension
    # TODO: We need to keep in mind that the pixel size should change with
    # upsampling
    points = [(col*tf[1], row*tf[5], channel[row][col])
              if channel[row][col] != no_value else
              (col*tf[1], row*tf[5], 0.)
              for row in range(channel.shape[0])
              for col in range(channel.shape[1])]

    # Create faces from grid. Basically this is just turning  a grid into
    # triangles
    for row in range(channel.shape[0]-1):
        for col in range(channel.shape[1]):
            if col is not channel.shape[1]-1:
                v1 = cnt
                v2 = cnt + 1
                v3 = cnt + channel.shape[1] + 1
                v4 = cnt + channel.shape[1]

                faces.append(([v1, v2, v3], 0, 0, 0))
                faces.append(([v1, v4, v3], 0, 0, 0))

            cnt = cnt + 1

    # Create np array for turning vertices and faces into a ply file
    faces = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                   ('red', 'u4'),
                                   ('green', 'u4'),
                                   ('blue', 'u4')])

    vertices = np.array(points, dtype=[('x', 'f4'),
                                       ('y', 'f4'),
                                       ('z', 'f4')])

    # Write data to new file
    el = PlyElement.describe(vertices, 'vertex')
    el2 = PlyElement.describe(faces, 'face')

    PlyData([el, el2], text=True).write(plyfile)

    return channel.shape


if __name__ == "__main__":
    print(tif2mesh("../data/tif/black_mtn_alos.tif",
                   "../data/tif/black_mtn_alos.ply",
                   4, 3))
