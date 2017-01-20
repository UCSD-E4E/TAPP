from osgeo import gdal
import subprocess

# GDAL affine transform parameters, According to gdal
# documentation xoff/yoff are image left corner, a/e are pixel wight/height
# and b/d is rotation and is zero if image is north up.


def pixel2coord(gt, x, y):
    """Returns global coordinates from pixel x, y coordinates"""
    lat = gt[0] + x*gt[1] + y*gt[2]
    lon = gt[3] + x*gt[4] + y*gt[5]

    return lat, lon


def coord2pixel(gt, lat, lon):
    """Transforms lat/lon coordinates to pixel coordinates"""
    x = int(round((lat-gt[0])/gt[1]))
    y = int(round((lon-gt[3])/gt[5]))

    return x, y


def trim(lat1, lon1, lat2, lon2, infile, outfile):
    '''

    '''
    transform = gdal.Open(infile).GetGeoTransform()

    x1, y1 = coord2pixel(transform, lat1, lon1)
    x2, y2 = coord2pixel(transform, lat2, lon2)

    args = ['gdal_translate', '-srcwin']
    args.extend([str(x1), str(y1), str(x2-x1), str(y2-y1), infile, outfile])

    ls_output = subprocess.call(args)
    print(ls_output)

if __name__ == "__main__":
    data_set = gdal.Open('../data/canyon_dem_utm11.tif')
    gt = data_set.GetGeoTransform()

    lat1, lon1 = pixel2coord(gt, 0, 0)
    lat2, lon2 = pixel2coord(gt, 10, 10)
    trim(lat1, lon1, lat2, lon2, '../data/canyon_dem_utm11.tif', '../data/test.tif')

    print(pixel2coord(gt, 1, 1))
    print(coord2pixel(gt, 478279.930, 3638571.112))
    x, y = pixel2coord(gt, 100, 1220)
    print(coord2pixel(gt, x, y))
