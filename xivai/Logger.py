class Logger(object):
	
	def __init__(self, fname):
		self.keys = []
		self.logs = {}
		self.dumping = False
		self.fp = open(fname, "w")

	def add(self, key, value):
		self.logs[key] = value
		if(self.dumping == False):
			self.keys.append(key)

	def dump(self):
		if(self.dumping == False):
			for key in self.keys:
				self.fp.write(str(key) + ",")
			self.fp.write("\n")
			self.dumping = True

		for key in self.keys:
			self.fp.write(str(self.logs[key]) + ",")
		self.fp.write("\n")
		self.fp.flush()
		self.logs = {}

	def clear(self):
		if(self.dumping == False):
			self.keys = []
		self.logs = {}

	def close(self):
		self.fp.close()
