from DamageTable import DamageTable
import libs

class BattleData(object):
	def __init__(self):
		self.action = {}
		self.table = None

	def clear(self):
		self.time = 0.0
		self.recast = {}
		self.damage = {}
		self.state = {}
		self.casting = None
		self.before = None
		self.plan = None
		self.history = []
		self.reserve = []

	def getAmp(self):
		return self.getPureAmp() * self.getCritAmp() * self.getDirecAmp()

	def getPureAmp(self):
		amp = 1.0
		for act in self.state.values():
			if(act.isValid() and act.amp > libs.eps):
				amp *= act.amp
		return amp

	def getHaste(self):
		haste = 1.0
		for act in self.state.values():
			if(act.isValid() and act.haste > libs.eps):
				haste *= act.haste
		return haste

	def getCritProb(self):
		prob = self.table.baseCritProb
		for act in self.state.values():
			if(act.isValid() and act.crit > libs.eps):
				prob *= act.crit
				if(act.crit >= 10):
					return 1.0
				if(prob >= 1.0):
					return 1.0
		return prob

	def getCritAmp(self):
		return libs.calcExpect(self.getCritProb(), self.table.baseCritAmp)

	def getDirecProb(self):
		prob = self.table.baseDirecProb
		for act in self.state.values():
			if(act.isValid() and act.direc > libs.eps):
				prob *= act.direc
				if(act.direc >= 10):
					return 1.0
				if(prob >= 1.0):
					return 1.0
		return prob

	def getDirecAmp(self):
		return libs.calcExpect(self.getDirecProb(), self.table.baseDirecAmp);

