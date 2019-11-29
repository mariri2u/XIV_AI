from action.GCDAction import GCDAction
from action.Ability import Ability

def getWhmActions():
	actions = [
			GCDAction("ストンジャ", power=250, cast=1.0),
#			GCDAction("ストンガ", power=210, cast=1.0),
#			GCDAction("ストンラ", power=200, cast=1.0)
			GCDAction("エアロラ", power=50, slip=50, duration=18),
			GCDAction("エアロガ", power=50, slip=40, duration=24, cast=1.0),
			Ability("アサイズ", power=400, recast=45),
			Ability("クルセードスタンス", amp=1.05, recast=90, duration=15)
		]
	return actions