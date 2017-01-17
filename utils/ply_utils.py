from plyfile import PlyData, PlyElement
import numpy as np

# Guide to ply format can be found at http://paulbourke.net/dataformats/ply/
# TODO add another function that lets you work with colors before writing it to
# file


def ply_colorize(filename):
    """
    This function takes a ply that does not contain colored faces and convert
    it to a colored file format. Note that if you want to work with the colors
    you must reread the new file.
    """

    # Read data from existing ply
    plydata = PlyData.read(filename+".ply")

    # Return false if the file already contains colored faces
    properties = str(plydata['face'].properties)
    if "red" and "green" and "blue" in properties:
        print("PLY File already contains colored faces")
        return False

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

    PlyData([el, el2], text=True).write(filename+"_colored.ply")

    return True
