from plyfile import PlyData, PlyElement
import numpy as np
import numpy.lib.recfunctions as rfn

# Guide to ply format can be found at http://paulbourke.net/dataformats/ply/
# TODO add another function that lets you work with colors before writing it to
# file


def ply_face2vertices(face, vertices):
    vert1 = np.asarray([vert for vert in vertices[face[0]]])
    vert2 = np.asarray([vert for vert in vertices[face[1]]])
    vert3 = np.asarray([vert for vert in vertices[face[2]]])

    return vert1, vert2, vert3


def ply_colorize(filename):
    """
    This function takes a ply that does not contain colored faces and convert
    it to a colored file format. Note that if you want to work with the colors
    you must reread the new file.

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
    # if "red" and "green" and "blue" and "counter" in properties:
        # return True

    faces = plydata['face'].data
    vertices = plydata['vertex'].data

    # Create new set of faces with color attribute
    # NOTE: This may take a while for large mesh files
    faces = [(face[0].tolist(), 0, 0, 0, 0) for face in faces]

    faces = np.array(faces, dtype=[('vertex_indices', 'i4', (3,)),
                                   ('counter', 'i4'),
                                   ('red', 'u1'),
                                   ('green', 'u1'),
                                   ('blue', 'u1')])

    # Write data to new file
    el = PlyElement.describe(vertices, 'vertex')
    el2 = PlyElement.describe(faces, 'face')

    PlyData([el, el2], text=True).write(filename)

    return True


def ply_add_properties(filename, element, properties, value):
    """
    This function takes a ply file and attempts to add properties to an
    elements. One common example is adding colors to the face elements or
    adding a counter.

    Example:

    Args:
        element (string): The name of the element you are adding a property to.

        properties ([] string): The names of the properties you adding. It
        should come in the form of a list of tuples i.e. ('red', 'u1')

        value (float): Default value for the propertie to start with.

    Returns:
        boolean: Returns true if the properties we successfully added false
        otherwise.

    """

    # Read data from existing ply
    plydata = PlyData.read(filename)

    # Return false if the file already contains colored faces
    # TODO FIX
    # if set(properties) < set(str(plydata[element].properties)):
    #     return False

    # TODO This only covers these two types of elements
    faces = plydata['face'].data
    vertices = plydata['vertex'].data

    # Create new set of faces with color attribute
    # NOTE: This may take a while for large mesh files
    new_faces = []
    for face in faces:
        new_face = [face[0].tolist()]
        new_face.extend([value for prop in properties])
        new_faces.append(tuple(new_face))

    print(faces.dtype.fields, faces.dtype.names[0])
    # for idx in range(len(faces.dtype.names)):
        # print(faces.dtype.names[idx], faces.dtype.fields[idx])

    data_types = []
    for t in range(len(faces.dtype)):
        print(t, faces.dtype[t])
        data_types.append(faces.dtype[t])

    print(data_types)
    data_types.extend(properties)

    # TODO Figure out how to set the properities here
    faces = np.array(new_faces, dtype=data_types)
    # faces = np.array(new_faces, dtype=[('vertex_indices', 'i4', (3,)),
    #                                ('red', 'u1'),
    #                                ('green', 'u1'),
    #                                ('blue', 'u1')])

    # Write data to new file
    el = PlyElement.describe(vertices, 'vertex')
    el2 = PlyElement.describe(faces, 'face')

    PlyData([el, el2], text=True).write(filename.strip(".ply")+"_colored.ply")

    return True
