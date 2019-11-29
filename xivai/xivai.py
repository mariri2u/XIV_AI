import numpy as np
import libs
from BattleManager import BattleManager
from AI import AI

from config import whm

import numpy as np

actions = whm.getWhmActions()

ai = AI(actions, 30)
ai.training = True

bm = BattleManager()
bm.preInit(2.41, libs.getHealerTable(), actions, ai)

for gen in range(100):
	fname = "log/whm_" + str(gen) + "th.csv"

	bm.init(fname)

#	for time in range((int)(180/libs.delta)):
	while bm.totalDmg < 600000:
		bm.step()

	dps = bm.calcDPS()
	bm.close()

	print(gen, "th DPS is", dps, "time is", bm.time)

	ai.train(dps)
	print("statistics", ai.statistics())
	

print("Learn Finished.")

ai.finish()
ai.save("log/whm_agent")

bm.init("log/whm_final.csv")

for time in range((int)(600/libs.delta)):
	bm.step()

print("Finally DPS is ", bm.calcDPS())
bm.close()
