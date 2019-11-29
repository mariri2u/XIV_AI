from action.Action import Action
import libs

class GCDAction(Action):
	def applyGlobal(self, gcd):
		self.recast = gcd
		self.cast *= gcd
		self.motion = 0.1

	def canAction(self):
		if(super().canAction() and self.data.recast["global"] < libs.eps):
			return True
		else:
			return False

	def calcAction(self):
		self.data.recast["global"] = self.data.getHaste() * (self.recast - self.cast)
		if(self.combo):
			self.data.before = self
