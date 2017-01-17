#!/usr/bin/env python3

# Code derived from "Fast, Minimum storage Ray / Triangle Intersection" by
# Tomas Moller and Ben Trumbore

from plyfile import PlyData, PlyElement
import numpy as np

EPSILON = .000001

# One sided triangle
# def raytri_intersect(orig, dir, vert0, vert1, vert2):
#     edge1 = vert1 - vert0
#     edge2 = vert2 - vert0
#
#     pvec = np.cross(dir, edge2)
#     det  = np.dot(edge1, pvec)
#
#     if det < EPSILON:
#         return 0
#
#     tvec = orig - vert0
#
#     u = np.dot(tvec, pvec)
#
#     if u < 0. or u > det:
#         return 0
#
#     qvec = np.cross(tvec, edge1)
#
#     v = np.dot(dir, qvec)
#
#     if v < 0. or (u + v) > det:
#         return 0
#
#     t = np.dot(edge2, qvec)
#     inv_det = 1. / det;
#     t = t*inv_det
#     u = u*inv_det
#     v = v*inv_det
#
#     return 1


# Two sided triangle
def raytri_intersect(orig, dir, vert0, vert1, vert2):
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

# Simple test demonstrating how to color a triangle given an intersection
if __name__ == '__main__':

    # Make sure the .ply file has colored faces
    ply_colorize("../data/small_plane_colored")

    # Read data from existing ply
    plydata = PlyData.read("../data/small_plane_colored.ply")

    faces = plydata['face'].data
    vertices = plydata['vertex'].data

    # Setup a fake origin
    orig = np.array([.5, .5, 10])
    dvec = np.array([0, 0, -1])

    # If hit color red
    for face in faces:
        vert0 = np.array([v for v in vertices[face[0][0]]])
        vert1 = np.array([v for v in vertices[face[0][1]]])
        vert2 = np.array([v for v in vertices[face[0][2]]])

        res = raytri_intersect(orig, dvec, vert0, vert1, vert2)
        if res:
            face[1] = 255
            face[2] = 0
            face[3] = 0

    # Write ply back to file
    el = PlyElement.describe(vertices, 'vertex')
    el2 = PlyElement.describe(faces, 'face')

    PlyData([el, el2], text=True).write("../data/small_plane_colored2.ply")
