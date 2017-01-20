#!/usr/bin/env python3

import os
import sys
import unittest
import numpy as np

from ..TAPP import Camera


class CameraTest(unittest.TestCase):

    def setUp(self):
        self.c1 = Camera.Camera("data/small_plane.ply", 40., 5., 5., "TEST_CAMERA")
        # self.c1 = Camera.Camera("data/textured_plane.ply", 50., 50., 50., "TEST_CAMERA")

    def test_create_rays(self):
        self.c1._create_rays()

        print(len(self.c1._rays))
        # print csv to file for debugging w/matlab
        with open("rays.out", "w") as outfile:
            for ray in self.c1._rays:
                line = str(ray[0])+","+str(ray[1])+","+str(ray[2])+"\n"
                outfile.write(line)

    def test_intersection(self):
        self.c1._create_rays()
        print("")
        self.c1.snap(np.array([0, 0, 1]))

if __name__ == '__main__':
    unittest.main()
