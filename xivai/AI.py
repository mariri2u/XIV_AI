import numpy as np

import chainer
import chainer.functions as F
import chainer.links as L
from chainer import cuda, Function, gradient_check, report, training, utils, Variable
from chainer import datasets, iterators, optimizers, serializers
from chainer import Link, Chain, ChainList
from chainer.training import extensions
import chainerrl

import random

from action.GCDAction import GCDAction
from action.Ability import Ability

class QFunction(Chain):
	def __init__(self, obs_size, n_action, n_hidden_channels=50):
		super(QFunction, self).__init__(
				l0 = L.Linear(obs_size, n_hidden_channels),
				l1 = L.Linear(n_hidden_channels, n_hidden_channels),
				l2 = L.Linear(n_hidden_channels, n_hidden_channels),
				l3 = L.Linear(n_hidden_channels, n_action),
#				l4 = L.Linear(n_hidden_channels, n_action)
			)

	def __call__(self, x, test=False):
		h = F.tanh(self.l0(x))
		h = F.tanh(self.l1(h))
		h = F.tanh(self.l2(h))
#		h = F.tanh(self.l3(h))
#		h = F.relu(self.l0(x))
#		h = F.relu(self.l1(h))
#		h = F.relu(self.l2(h))
#		h = F.leaky_relu(self.l0(x))
#		h = F.leaky_relu(self.l1(h))
#		h = F.leaky_relu(self.l2(h))
#		h = F.sigmoid(self.l0(x))
#		h = F.sigmoid(self.l1(h))
#		h = F.sigmoid(self.l2(h))
		return chainerrl.action_value.DiscreteActionValue(self.l3(h))

class AI():

	def __init__(self, actions, hidden=100):
		self.n_input = 2
		self.n_action = len(actions)
		self.training = True

		self.max_dps = 0.0
		self.step_dps = 0.0

		gpu_device = 0
		cuda.get_device(gpu_device).use()
		xp = cuda.cupy

		for act in actions:
			if(act.duration > 0):
				self.n_input += 1
			if(act.max > 0):
				self.n_input += 1
			if(act.slip > 0):
				self.n_input += 1
			if(isinstance(act, Ability)):
				self.n_input += 1

		self.x_data = xp.array([0]*self.n_input, dtype=xp.float32)

		index = 1
		self.x_data[0] = 0.0

		for i in range(self.n_action):
			act = actions[i]

			if(act.duration > 0):
				index += 1
				self.x_data[index] = 0.0
			if(act.max > 0):
				index += 1
				self.x_data[index] = 0.0
			if(act.slip > 0):
				index += 1
				self.x_data[index] = 0.0
			if(isinstance(act, Ability)):
				index += 1
				self.x_data[index] = 0.0

		q_func = QFunction(self.n_input, self.n_action, hidden)
		q_func.to_gpu(gpu_device)

		optimizer = chainer.optimizers.Adam(alpha=1e-3, weight_decay_rate=0.1, eps=1e-7)
#		optimizer = chainer.optimizers.Adam(alpha=0.01, weight_decay_rate=0.1, eps=1e-7)
#		optimizer = chainer.optimizers.SGD(lr=1e-3)
#		optimizer = chainer.optimizers.RMSprop(lr=1e-3, alpha=0.01)
#		optimizer = chainer.optimizers.AdaGrad(lr=1e-2, eps=1e-7)
		optimizer.setup(q_func)

		gamma = 0.95
#		explorer = chainerrl.explorers.ConstantEpsilonGreedy(
#			epsilon=0.0, random_action_func=self.randint)
		explorer = chainerrl.explorers.LinearDecayEpsilonGreedy(
			start_epsilon=0.3, end_epsilon=0.05, decay_steps=3000,random_action_func=self.randint)

		replay_buffer = chainerrl.replay_buffer.ReplayBuffer(capacity=10**6)

		phi = lambda x: x.astype(xp.float32, copy=False)

		self.agent = chainerrl.agents.DoubleDQN(
				q_func, optimizer, replay_buffer, gamma, explorer,
				replay_start_size=500, phi=phi
			)

	def start(self):
		pass

	def calc(self, data, dps):
		self.x_data[0] = data.getAmp() - 1.0

		index = 1

		for i in range(self.n_action):
			act = data.action[i]
			if(act.duration > 0):
				index += 1
				value = act.remain if act.remain > 0 else 0.0
				value = value - act.cast - data.recast["global"]
				value = value if value > 0 else 0.0
				value = value / act.duration
				value = 1 - value
#				self.x_data[index] = -1 * (1.5 + act.cast - act.remain) if act.remain >= 0.0 else 1.5 + act.cast
				self.x_data[index] = value
			if(act.max > 0):
				index += 1
				self.x_data[index] = 1 - (act.stack / act.max)
#				self.x_data[index] = act.stack if act.max > 0 else -1.0
			if(act.slip > 0):
				index += 1
				self.x_data[index] = act.slipAmp - 1.0 if act.slip > 0 else -1.0
			if(isinstance(act, Ability)):
				index += 1
				value = data.recast[act.name] if data.recast[act.name] >= 0.0 else 0.0
				value = 1 - (value / act.recast)
				self.x_data[index] = value
#				self.x_data[index] = -1 * data.recast[act.name] if data.recast[act.name] >= 0.0 else 0.0

		reward = 0
		if(self.step_dps != 0):
			reward = (dps / self.step_dps - 1.0) * 10
#		if(dps > self.step_dps):
#			reward = 1
#		elif(dps < self.step_dps * 0.9):
#			reward = -1

		self.step_dps = dps

		if(training):
			act = self.agent.act_and_train(self.x_data, reward)
		else:
			act = self.agent.act(self.x_data)

		return act

	def train(self, dps):
		reward = 0
		if(self.max_dps != 0):
			reward = (dps / self.max_dps - 1.0) * 10

#		if(dps > self.max_dps):
#			reward = 1
#		elif(dps < self.max_dps * 0.9):
#			reward = -1

		if(dps > self.max_dps):
			self.max_dps = dps
			self.agent.save("log/max_dps")

		self.agent.stop_episode_and_train(self.x_data, reward)
		self.step_dps = 0.0

	def close(self):
		pass

	def save(self, fname):
		self.agent.save(fname)

	def randint(self):
		return random.randint(0, self.n_action-1)

	def statistics(self):
		return self.agent.get_statistics()

	def finish(self):
		self.training = False
		self.agent.load("log/max_dps")
