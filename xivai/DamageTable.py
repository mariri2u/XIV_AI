class DamageTable():
	baseCritProb = 0.15
	baseCritAmp = 1.5
	baseDirecProb = 0.0
	baseDirecAmp = 1.15

	def __init__(self, x0, x1, y0, y1):
		self.__x0 = x0
		self.__x1 = x1
		self.__y0 = y0
		self.__y1 = y1

	def calc(self, x):
		return self.__y0 + (self.__y1 - self.__y0) * (x - self.__x0) / (self.__x1 - self.__x0)
