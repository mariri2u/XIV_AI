from action.Action import Action
import libs

class Ability(Action):
	def canAction(self):
		if(super().canAction() and self.data.recast[self.name] < libs.eps):
			return True
		else:
			return False

	def calcAction(self):
		self.data.recast[self.name] = self.recast
