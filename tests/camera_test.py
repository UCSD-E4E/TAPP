#!/usr/bin/env python3

import os
import sys
import unittest

from ..TAP import Camera


class CameraTest(unittest.TestCase):

    def setUp(self):
        self.c1 = Camera.Camera(40., 5., 5., "TEST_CAMERA")

    def test_create_rays(self):
        self.c1._create_rays()

        # print csv to file for debugging w/matlab
        for ray in self.c1.rays:
            line = str(ray[0])+","+str(ray[1])+","+str(ray[2])
            print(line)

if __name__ == '__main__':
    unittest.main()
