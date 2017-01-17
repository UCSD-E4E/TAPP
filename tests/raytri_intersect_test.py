#!/usr/bin/env python3

import os
import sys
import unittest
import numpy as np

from ..TAP import raytri_intersect as ry


class RayTriIntersectTest(unittest.TestCase):

    # Define a basic triangle
    def setUp(self):
        self.vert0 = np.array([0, 0, 0])
        self.vert1 = np.array([1, 0, 0])
        self.vert2 = np.array([1, 1, 0])

    # Tests if origin lies above the triangle
    def test_above(self):
        orig = np.array([.5, .5, 10])
        dvec = np.array([0, 0, -1])

        res = ry.raytri_intersect(orig, dvec, self.vert0,
                                  self.vert1, self.vert2)

        self.assertEqual(res, 1)

    # Tests if the origin lies below the triangle
    def test_below(self):
        orig = np.array([.5, .5, -10])
        dvec = np.array([0, 0, 1])

        res = ry.raytri_intersect(orig, dvec, self.vert0,
                                  self.vert1, self.vert2)

        self.assertEqual(res, 1)

    # Tests if ray intersects with edges of corners
    # TODO do this
    def test_corners(self):
        orig = np.array([.5, .5, -10])
        dvec = np.array([0, 0, 0])

        res = ry.raytri_intersect(orig, dvec, self.vert0,
                                  self.vert1, self.vert2)

        self.assertEqual(res, 1)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
