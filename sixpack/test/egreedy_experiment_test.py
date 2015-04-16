from __future__ import print_function
import unittest
import fakeredis
from mabtester import MABTester
from sixpack.models import Experiment, MABEGreedyExperiment, Alternative, Client

import sys

class TestMABEGreedyExperiment(unittest.TestCase):

    unit = True

    def setUp(self):
        self.redis = fakeredis.FakeStrictRedis()

    def test_egreedy(self):
        tester = MABTester("test", MABEGreedyExperiment, ["red", "blue"], 50, 250, redis=self.redis)
        self.assertTrue(tester.test())
