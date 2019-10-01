from settings import NONBACKGROUND

class Configuration:
	def __init__(self,normaliseBySBM,expBackgroundCorrection):
		self.normaliseBySBM = normaliseBySBM
		self.expBackgroundCorrection = expBackgroundCorrection
