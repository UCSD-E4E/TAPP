#!/usr/bin/env python

import pymesh


class coverage_analyzer:
	def __init__(self, camera):
		"""Create a new coverage_analyzer object with the specified camera"""
		self.cam_param = camera;

	def analyze(mesh, poses):
		for pose in poses:
			seen_vertices = self.cam_param.snap(pose)
			for 
