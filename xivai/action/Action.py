import libs

class Action(object):
	@property
	def stack(self):
		return self.__stack
	
	@stack.setter
	def stack(self, stack):
		if(stack > max):
			self.__stack = self.max
		else:
			self.__stack = stack


	def __init__(self, name=None, *, 
			power=0, cast=0.0, recast=0.0, motion=0.8, slip=0, duration=0, require=0, increase=0, max=0,
			relation=None, relationA=None, relationB=None, relationC=None, before=None, combo=True,
			amp=0.0, haste=0.0, crit=0.0, direc=0.0):
		# 固定値
		self.name = name
		self.power = power
		self.cast = cast
		self.recast = recast
		self.motion = motion
		self.slip = slip
		self.duration = duration
		self.require = require
		self.increase = increase
		self.max = max
		self.relation = relation
		self.relationA = relationA
		self.relationB = relationB
		self.relationC = relationC
		self.before = before
		self.combo = combo

		self.amp = amp
		self.haste = haste
		self.crit = crit
		self.direc = direc

		# 状態量
		self.remain = 0.0
		self.slipAmp = 1.0
		self.__stack = 0

		self.data = None

	def clear(self):
		self.remain = 0.0
		self.slipAmp = 1.0
		self.__stack = 0

	def canAction(self):
		if(self.inMotion() and self.inRelation() and self.inBefore()):
			return True
		else:
			return False

	def inMotion(self):
		if(self.data.recast["cast"] < libs.eps and self.data.recast["motion"] < libs.eps):
			return True
		else:
			return False

	def inRelation(self):
		if(self.relation == None):
			return True
		elif(self.require == 0):
			return True
		elif(self.relation in self.data.state and self.data.state[relation].stack >= self.require):
			return True
		else:
			return False

	def inBefore(self):
		if(self.before == None):
			return True
		elif(self.data.before != None and self.data.before.name == self.before):
			return True
		else:
			return False

	def isValid(self):
		result = False

		if(self.duration > libs.eps):
			if(self.remain > libs.eps):
				result &= True
			else:
				result &= False

		if(self.max > 0):
			if(self.stack > 0):
				result &= True
			else:
				result &= False

		return result

	def startAction(self):
		if(self.cast > libs.eps):
			self.data.recast["cast"] = self.data.getHaste() * self.cast
			self.data.casting = self
		else:
			self.doneAction()

	def doneAction(self):
		self.data.plan = self

		self.calcAction()
		self.data.casting = None

		if(self.power > 0):
			self.data.damage["action"] = self.data.getAmp() * self.data.table.calc(self.power)

		if(self.slip > 0):
			self.slipAmp = self.data.getAmp()

		if(self.duration > 0):
			self.remain = self.duration

		if(self.max > 0):
			self.stack = self.max

		if(self.relation != None):
			self.calcRelation()

		if(self.data.recast["motion"] < self.motion):
			self.data.recast["motion"] = self.motion

		self.data.history.append(self)
		self.data.plan = None

	def calcRelation(self):
		if(self.increase > 0):
			self.data.state[relation].stack += self.increase

		if(self.require > 0):
			self.data.state[relation].stack -= self.require

	def calcAction(self):
		pass

	def tick(self):
		if(self.slip > 0 and self.data.recast["dot"] < libs.eps):
			self.data.damage["dot"] += self.slipAmp * self.data.table.calc(self.slip)

	def doneStep(self):
		pass


