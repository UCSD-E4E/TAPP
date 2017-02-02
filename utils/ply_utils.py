from plyfile import PlyData, PlyElement

import numpy as np
import numpy.lib.recfunctions as rfn


def face2vertices(face, vertices):
    vert1 = np.asarray([vert for vert in vertices[face[0]]])
    vert2 = np.asarray([vert for vert in vertices[face[1]]])
    vert3 = np.asarray([vert for vert in vertices[face[2]]])

    return vert1, vert2, vert3


def colorize(filename):
    """
    This function takes a ply that does not contain colored faces and convert
    it to a colored file format. Note that if you want to work with the colors
    you must reread the new file. Useful http://paulbourke.net/dataformats/ply/

    Args:
        filename (str): The filename of the ply file including the prefex .ply

    Returns:
        boolean: Returns true if the properties we successfully added false
        otherwise.
    """
    # Read data from existing ply
    plydata = PlyData.read(filename)

    # Return false if the file already contains colored faces
    properties = str(plydata['face'].properties)

    if "red" and "green" and "blue" and "counter" in properties:
        return True

    faces = plydata['face'].data
    vertices = plydata['vertex'].data

    # Create new set of faces with color attribute
    # NOTE: This may take a while for large mesh files
    faces = [(face[0].tolist(), 0, 0, 0) for face in faces]

    faces = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                   ('red', 'u1'),
                                   ('green', 'u1'),
                                   ('blue', 'u1')])

    # Write data to new file
    el = PlyElement.describe(vertices, 'vertex')
    el2 = PlyElement.describe(faces, 'face')

    PlyData([el, el2], text=True).write(filename)

    return True
