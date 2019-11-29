from DamageTable import DamageTable

eps = 1.0e-7
dotTick = 3.0
delta = 0.01
timeout = 3.0
fps = (int)(1 / delta)

def calcExpect(prob, maxamp):
	amp = 1.0
	if(prob <= 0.0):
		amp = 1.0
	elif(prob >= 1.0):
		amp = maxamp
	else:
		amp = 1.0 + (maxamp - 1.0) * prob
	return amp

def getTankTable():
	table = getPhysicTable()
	table.baseDirecProb = 0.0
	return table

def getPhysicTable():
	table = DamageTable(150, 540, 3000, 11200)
	table.baseDirecProb = 0.3
	return table

def getMagicTable():
	table = DamageTable(50, 220, 1900, 8000)
	table.baseDirecProb = 0.3
	return table

def getHealerTable():
	table = getMagicTable()
	table.baseDirecProb = 0.0
	return table

