import math
import numpy as np

from plyfile import PlyData, PlyElement
from utils import ply_utils


class Camera(object):
    """Camera will take pictures"""
    def __init__(self, infile, fov, width, height, _id):
        self.fov = fov
        self.width = width
        self.height = height

        self._rays = []
        self._infile = infile
        self._id = _id

        # TODO: Decide what should happen here
        try:
            self._plydata = PlyData.read(infile)
        except Exception as ex:
            print(str(ex))

    # TODO: Create pose class which constitutes rpy, lla, coordinate frame and
    # perform transforms between local and global
    def snap(self, pose):
        """
        Takes a 'picture' of the what the camera can see given a position and
        orientation by through find ray-triangle intersection with the vertices

        Args:
            pose (numpy array float64): This constitutes 6 DOF with the first
                three in the array representing the location x, y, and zed and
                the last three representing the roll, pitch, and yaw.

            vertices (plydata): A custom data structure that holds vertice
                locations as well as a list of vertice triplets that make up
                the triangles.

        """
        # TODO: Should this be its own class variable so that its not created
        # each time. Basically need to figure out the best way to store
        # the ply file. This is probably not going to be on disk and it may
        # not be inside this class either.
        faces = self._plydata['face'].data
        vertices = self._plydata['vertex'].data

        for face in faces:
            vert0, vert1, vert2 = \
                ply_utils.face2vertices(face[0], vertices)

            # TODO: Come up with coloring schema
            for idx, ray in enumerate(self._rays):
                ret = self._check_intersection(pose, ray, vert0, vert1, vert2)
                face[1] = face[1] + ret
                face[2] = face[2] + ret

        self._plydata['face'].data = faces

    def closePly(self):
        self._plydata.write(self._infile.strip(".ply")+"_new.ply")

    def _create_rays(self):
        """
        This method should simply create an 2D array of unit vectors where
        each vector corresponds to a 'ray' entering the camera based on the
        field of view and the resolution of the image.

        Derived from "https://www.scratchapixel.com/lessons/3d-basic-rendering/
        ray-tracing-generating-camera-rays/generating-camera-rays"
        """

        for y in range(int(self.height)):
            for x in range(int(self.width)):
                # assuming width>height
                aspect_ratio = self.width / self.height
                Px = (2 * ((x + 0.5) / self.width) - 1) \
                    * math.tan(self.fov / 2 * math.pi / 180) * aspect_ratio

                Py = (1 - 2 * ((y + 0.5) / self.height)) \
                    * math.tan(self.fov / 2 * math.pi / 180)

                origin = np.array([0., 0., 0.])

                ray = (np.array([Px, Py, -1]) - origin) \
                    / math.sqrt(Px*Px + Py*Py + 1)

                self._rays.append(ray)

    # TODO: Decide what happens when a ray intersects exactly on a boundary.
    # Possibly could just allow it to double count the hit for both
    def _check_intersection(self, orig, dir, vert0, vert1, vert2):
        """
        Ray Triangle Intersection alogrithm derived from "Fast, Minimum storage
        Ray / Triangle Intersection" by Tomas Moller and Ben Trumbore. Two
        sided version, alternatively a one sided version where an Intersection
        only occurs if entering the 'top' of the triangle described by the
        vertices.

        Args:
            orig (numpy array float64): Position x, y, and zed in the world
                frame.

            dir (numpy array float64): 3D Vector in the world frame.

            vert0-2 (numpy array float64): Position x, y, and zed in the world
                frame for each of the three vertices.

        Returns:
            int: The return code:
                0 - No intersection
                1 - Intersection
        """

        EPSILON = .000000001

        edge1 = np.subtract(vert1, vert0)
        edge2 = np.subtract(vert2, vert0)

        pvec = np.cross(dir, edge2)
        det = np.dot(edge1, pvec)

        if det > -EPSILON and det < EPSILON:
            return 0

        inv_det = 1. / det

        tvec = np.subtract(orig, vert0)

        u = np.dot(tvec, pvec) * inv_det

        if u < 0. or u > 1.0:
            return 0

        qvec = np.cross(tvec, edge1)

        v = np.dot(dir, qvec) * inv_det

        if v < 0. or u + v > 1.:
            return 0

        t = np.dot(edge2, qvec) * inv_det

        return 1
