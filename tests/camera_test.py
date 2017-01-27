
import os
import sys
import unittest
import numpy as np

from TAPP import Camera


class CameraTest(unittest.TestCase):

    def setUp(self):
        self.c1 = Camera.Camera("data/ply/black_mtn_alos.ply",
                                40., 1., 1.,
                                "TEST_CAMERA")
        self.c1._create_rays()

    def test_intersection(self):
        self.c1.snap(np.array([10, -20, 300]))


if __name__ == '__main__':
    unittest.main()
