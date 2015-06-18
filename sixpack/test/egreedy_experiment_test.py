from __future__ import print_function
import unittest
import fakeredis
from mabtester import MABTester
from sixpack.models import Experiment, MABEGreedyExperiment, Alternative, Client

import sys

from sixpack.server import create_app


class TestMABEGreedyExperiment(unittest.TestCase):

	unit = True

	def setUp(self):
		self.app = create_app()
		# TODO: change this to fake-redis (msetbit script isn't registered with fakeredis currently)
		self.redis = self.app.redis

	def test_egreedy(self):
		tester = MABTester("test", MABEGreedyExperiment, ["red", "blue"], 50, 250, redis=self.redis)
		self.assertTrue(tester.test())
