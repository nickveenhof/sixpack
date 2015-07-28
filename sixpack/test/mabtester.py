
import random

from sixpack.models import Client, MABEGreedyExperiment

class BernoulliArm:
	def __init__ (self, p):
		self._p = p

	def draw(self):
		return random.random() > self._p and 1 or 0


class MABTester:
	def __init__ (self, name, experiment, alternatives, sims, horizon, redis):
		""" Initialize a new tester for the given experiment

		- name: the name of the experiment
		- experiment: the experiment class that needs to be tested
		- alternatives: the alternatives for the experiment
		- sims: the number of simulations
		- horizon: the number of clients in a simulation
		"""
		self._name = name

		means = [random.random() for alt in alternatives]
		self._best_arm = alternatives[means.index(max(means))]
		self._arms = {alt: BernoulliArm(means[idx]) for idx, alt in enumerate(alternatives)}

		self._experiment = experiment(name, alternatives, traffic_fraction=1, redis=redis)

		self._sims = sims
		self._horizon = horizon

		self._chosen_arms        = [0.0 for i in range(sims * horizon)]
		self._rewards            = [0.0 for i in range(sims * horizon)]
		self._cumulative_rewards = [0.0 for i in range(sims * horizon)]
		self._sim_nums           = [0.0 for i in range(sims * horizon)]
		self._times              = [0.0 for i in range(sims * horizon)]

	def test(self):
		for sim in range(self._sims):
			cumulative_reward = 0
			for t in range(self._horizon):
				index =  (sim * self._horizon) + t
				client = Client("%s" % index)

				self._sim_nums[index] = sim + 1
				self._times[index] = t + 1

				arm, policy = self._experiment.get_alternative(client)
				self._chosen_arms[index] = arm

				reward = self._arms[arm.name].draw()
				self._rewards[index] = reward

				cumulative_reward += reward
				self._cumulative_rewards[index] = cumulative_reward

				if reward == 1:
					self._experiment.convert(client, 1)
		return self._check_average_monotonicity()

	def _check_average_monotonicity (self):
		# indeces of the first client in each simulation
		idxs = [self._horizon * x for x in range(self._sims)]

		avgs = []
		for i in range(self._horizon):
			avgs.append(1.0 * sum([self._cumulative_rewards[idx] for idx in idxs]) / self._sims)
			idxs = [x + 1 for x in idxs]

		for i in range(1, len(avgs)):
			if avgs[i - 1] > avgs[i]:
				return False
		return True

	def save(self):
		pass






