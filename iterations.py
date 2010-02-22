import time

class IterationRegister(object):
	"""Registers algorithm iteration statistics"""
	def __init__(self):
		self._times = []
		self._start = None
		
	def start_iteration(self):
		self._start = time.clock()
		
	def end_iteration(self):
		self._times.append(time.clock() - self._start)
		assert(self._start is not None)
		self._start = None
		
	def get_max_iterationtime(self):
		return max(self._times)
	
	def get_min_iterationtime(self):
		return min(self._times)
		
	def get_avg_iterationtime(self):
		return sum(self._times)/len(self._times)