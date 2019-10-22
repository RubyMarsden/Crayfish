from settings import NONBACKGROUND

class Configuration:
	def __init__(self, normaliseBySBM, linear_background_correction):
		self.normaliseBySBM = normaliseBySBM
		self.linear_background_correction = linear_background_correction
