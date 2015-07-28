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

	def test_exploit_vs_explore(self):
		e = Experiment.find_or_create("exploit-vs-explore", "mab:egreedy", ["red", "blue"], traffic_fraction=1, explore_fraction=0.1, redis=self.redis)
		self.assertTrue(type(e) == MABEGreedyExperiment)

		e = Experiment.find_or_create("exploit-vs-explore", "mab:egreedy", ["red", "blue"], traffic_fraction=1, explore_fraction=0.1, redis=self.redis)
		self.assertTrue(type(e) == MABEGreedyExperiment)

	def test_egreedy(self):
		tester = MABTester("test", MABEGreedyExperiment, ["red", "blue"], 50, 250, redis=self.redis)
		self.assertTrue(tester.test())
