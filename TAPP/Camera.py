import math
import numpy


class Camera(object):
    """Camera will take pictures"""
    def __init__(self, fov, width, height, _id):
        self.fov = fov
        self.width = width
        self.height = height
        self.rays = []
        self._id = _id

    # TODO: Create pose class which constitutes rpy, lla, coordinate frame and
    # perform transforms between local and global
    def snap(self, pose, tri):
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

        Returns:
            []: List of vertices captured in the picture

        """
        for ray in self.rays:
            if self._check_intersection(pose, tri.v1, tri.v2, tri.v3):
                # Color triangle
                pass

        return

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

                origin = numpy.array([0., 0., 0.])

                ray = (numpy.array([Px, Py, -1]) - origin) \
                    / math.sqrt(Px*Px + Py*Py + 1)

                self.rays.append(ray)

    def _check_intersection(orig, dir, vert0, vert1, vert2):
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

        EPSILON = .000001

        edge1 = vert1 - vert0
        edge2 = vert2 - vert0

        pvec = np.cross(dir, edge2)
        det = np.dot(edge1, pvec)

        if det > -EPSILON and det < EPSILON:
            return 0

        inv_det = 1. / det

        tvec = orig - vert0

        u = np.dot(tvec, pvec) * inv_det

        if u < 0. or u > 1.0:
            return 0

        qvec = np.cross(tvec, edge1)

        v = np.dot(dir, qvec) * inv_det

        if v < 0. or u + v > 1.:
            return 0

        t = np.dot(edge2, qvec) * inv_det

        return 1
