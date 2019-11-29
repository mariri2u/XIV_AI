import libs

from Logger import Logger
from BattleData import BattleData
from action.Action import Action
from action.GCDAction import GCDAction
from action.Ability import Ability
import libs

import random

class BattleManager():
	def __init__(self):
		self.frameDmg = 0.0
		self.stepDmg = [0] * 3000

		self.data = BattleData()

	def preInit(self, gcd, table, actions, ai):

		self.data.table = table
		self.data.action = actions
		self.ai = ai

		self.data.clear()

		for act in self.data.action:
			act.data = self.data

			if(isinstance(act, GCDAction)):
				act.applyGlobal(gcd)

#			if(isinstance(act, AutoAttack)):
#				act.applySpeed(gcd)

	def init(self, fname):
		self.logs = Logger(fname)

		self.time = 0.0
		self.frame = 0
		self.totalDmg = 0
		self.timeout = 0.0

		self.data.clear()
		self.data.recast["aa"] = 0.0
		self.data.recast["global"] = 0.0
		self.data.recast["cast"] = 0.0
		self.data.recast["motion"] = 0.0
		self.data.recast["dot"] = libs.dotTick

		self.used = None
		self.reserve = None

		for act in self.data.action:
			if(isinstance(act, Ability)):
				self.data.recast[act.name] = 0.0
			if(act.duration > 0 or act.max > 0 or act.amp > libs.eps or act.haste > libs.eps or act.crit > libs.eps or act.direc > libs.eps):
				self.data.state[act.name] = act
			act.clear()

	def step(self):
		self.initStep()
		self.tick()
		self.actionDamage()
		self.mergeDamage()
		self.dump()
		self.stepToNext()

	def close(self):
		self.logs.close()

	def calcDPS(self):
		if(self.time < libs.eps):
			return 0
		else:
			return self.totalDmg / self.time

	def calcSecDPS(self, sec):
		dmg = 0.0
		end = (int)(self.frame / libs.fps - 1)
		start = (int)(end - sec)

		if(start < 0):
			start = 0

		if(end <= start):
			return 0.0

		for i in range(start, end):
			dmg += self.stepDmg[i]

		return dmg / (end - start)


	def initStep(self):
		self.used = None
		self.data.damage.clear()
		self.data.damage["dot"] = 0.0
		self.data.damage["action"] = 0.0

	def tick(self):
		for state in self.data.state.values():
			if(state.remain > libs.eps):
				state.tick()

		if(self.data.recast["dot"] < libs.eps):
			self.data.recast["dot"] = libs.dotTick

	def actionDamage(self):
		if(self.data.casting == None):
			if(self.reserve == None or self.timeout < libs.eps):
				id = self.ai.calc(self.data, self.calcDPS())
#				print("id:", id)
				self.reserve = self.data.action[id]
				self.timeout = libs.timeout
			
			if(self.reserve.canAction()):
				self.reserve.startAction()
				self.used = self.reserve
				self.reserve = None
				
		else:
			if(self.data.recast["cast"] < libs.eps):
				self.used = self.data.casting
				self.data.casting.doneAction()

	def mergeDamage(self):
		self.frameDmg = 0.0

		for key in self.data.damage.keys():
			self.frameDmg += self.data.damage[key]

		self.stepDmg[(int)(self.frame / libs.fps)] += self.frameDmg
		self.totalDmg += self.frameDmg

	def dump(self):
		if(self.frame % libs.fps == 0 or self.frameDmg > libs.eps or self.used != None):
			self.logs.add("time", self.time)

			if(self.used != None):
				self.logs.add("action", self.used.name)
#				print("time: ", self.time, "frame: ", self.frame, "action: ", self.used.name)
			else:
				self.logs.add("action", "none")

			if(self.reserve != None):
				self.logs.add("reserve", self.reserve.name)
			else:
				self.logs.add("reserve", "none")

			if(self.data.before != None):
				self.logs.add("before", self.data.before.name)
			else:
				self.logs.add("before", "none")

			self.logs.add("dmg.sec", self.stepDmg[(int)(self.frame / libs.fps)]);
			self.logs.add("dps.sec", self.calcSecDPS(15));
			self.logs.add("dmg.all", self.totalDmg);
			self.logs.add("dps.all", self.calcDPS());

			self.logs.add("pureamp", self.data.getPureAmp());
			self.logs.add("critprob", self.data.getCritProb());
			self.logs.add("critamp", self.data.getCritAmp());
			self.logs.add("direcprob", self.data.getDirecProb());
			self.logs.add("direcamp", self.data.getDirecAmp());
			self.logs.add("amp", self.data.getAmp());
			self.logs.add("haste", self.data.getHaste());

			for key in self.data.damage.keys():
				self.logs.add(key + ".damage", self.data.damage[key]);

			self.logs.add("damage", self.frameDmg);

			for key in self.data.state.keys():
				if (self.data.state[key].duration > 0):
					self.logs.add(key + ".remain", self.data.state[key].remain)

			for key in self.data.state.keys():
				if (self.data.state[key].max > 0):
					self.logs.add(key + ".stack", self.data.state[key].stack)

			for key in self.data.recast.keys():
				self.logs.add(key + ".recast", self.data.recast[key])

			self.logs.dump()
		else:
			self.logs.clear()

	def stepToNext(self):
		for key in self.data.recast.keys():
			self.data.recast[key] -= libs.delta

		for key in self.data.state.keys():
			self.data.state[key].doneStep()
			self.data.state[key].remain -= libs.delta

		self.frame += 1
		self.time += libs.delta
		self.data.time = self.time
		self.timeout -= libs.delta

