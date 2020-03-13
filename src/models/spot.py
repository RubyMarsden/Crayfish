from models.mathbot import *
from models.mass_peak import MassPeak
from models.settings import *

class Spot:

	def __init__(self, spot_data):

		self.name = spot_data[0][0]
		parts = self.name.split("-",1)
		if len(parts) != 2:
			raise Exception("None standard spot name in file '" + self.name + "'. Spot names must be of the form (SAMPLE)-(ID)")
		self.sample_name, self.id = parts

		self.numberOfScans = int(spot_data[1][4])
		self.numberOfPeaks = int(spot_data[1][6])
		self.sbmBackground = int(spot_data[1][15])
		self.mpNames = [row[0] for row in spot_data [4:4 + self.numberOfPeaks]]
		self.mpNamesBackground = [BACKGROUND1, BACKGROUND2]
		self.mpNamesNonBackground = [name for name in self.mpNames if name not in self.mpNamesBackground]
		self.uranium_peak_name = self.find_uranium_peak_name()
		self.mpCountTimes = {self.mpNames[i] : int(spot_data[i + 4][3]) for i in range(0, self.numberOfPeaks)}
		#self.is_standard = any([self.name.startswith(prefix) for prefix in config.standard_prefixes])
		#self.is_sample = any([self.name.startswith(prefix) for prefix in config.sample_prefixes])

		self.massPeaks = {}
		self.data = {}
		spot_number_of_rows = 5 + self.numberOfPeaks + self.numberOfScans * 2 * self.numberOfPeaks
		for i in range(0, self.numberOfPeaks):
			ithMpRows = []
			ithMpXValues = []
			ithSbmRows = []
			lineNumber = self.numberOfPeaks+5 + i*2
			mpName = self.mpNames[i]
			while lineNumber < spot_number_of_rows - 1:
				row = [float(value) for value in spot_data[lineNumber][4:14]]
				row2 = [int(value) for value in spot_data[lineNumber + 1][1:11]]
				ithMpRows.append(row)
				ithMpXValues.append(float(spot_data[lineNumber][1]))
				ithSbmRows.append(row2)
				lineNumber += self.numberOfPeaks*2

			massPeak = MassPeak(self.name,mpName,ithMpXValues,ithMpRows,ithSbmRows, self.mpCountTimes[mpName],self.numberOfScans)
			self.massPeaks[mpName] = massPeak

	def __repr__(self):
		return self.name

	def find_uranium_peak_name(self):
		for name in self.mpNamesNonBackground:
			if name.startswith("UO"):
				return name

		raise Exception("NO UO PEAK FOR SPOT " + self.name)


	def calculateMeanAndStDevForRows(self,inputKey,outputKey):
		for mp in self.massPeaks.values():
			mp.calculateMeanAndStDevForRows(inputKey,outputKey)

	def calculateCpsMeanAndStDevForRows(self, inputKey, outputKey):
		for mp in self.massPeaks.values():
			mp.calculateCpsMeanAndStDevForRows(inputKey, outputKey)

	def calculateBackgroundSubtractionSBMForRows(self):
		for mp in self.massPeaks.values():
			mp.calculateBackgroundSubtractionSBMForRows(self.sbmBackground)

	def normaliseToSBMForRows(self):
		for mp in self.massPeaks.values():
			mp.normaliseToSBMForRows()

	def subtractBackground2ForRows(self):
		for mp in self.massPeaks.values():
			if mp.mpName in self.mpNamesNonBackground:
				mp.subtractBackground2ForRows(self.massPeaks[BACKGROUND2], self.mpNamesNonBackground)

	def subtract_linear_background_for_rows(self):
		for mp in self.massPeaks.values():
			if mp.mpName == "ThO246":
				mp.subtract_linear_background_for_rows(self.massPeaks[BACKGROUND1],self.massPeaks[BACKGROUND2])
			elif mp.mpName in self.mpNamesNonBackground:
				mp.subtractBackground2ForRows(self.massPeaks[BACKGROUND2])

	def subtractExponentialBackgroundForRows(self):
		for mp in self.massPeaks.values():
			if mp.mpName == "ThO246":
				mp.subtractExponentialBackgroundForRows(self.massPeaks[BACKGROUND1],self.massPeaks[BACKGROUND2])
			elif mp.mpName in self.mpNamesNonBackground:
				mp.subtractBackground2ForRows(self.massPeaks[BACKGROUND2], self.mpNamesNonBackground)

	def calculateErrorWeightedMeanAndStDevForScans(self):
		for mpName in self.mpNamesNonBackground:
			self.massPeaks[mpName].calculateErrorWeightedMeanAndStDevForScans()
		
	def calculateActivityRatio(self):
		ThO246 = self.massPeaks["ThO246"]
		ThO248 = self.massPeaks["ThO248"]
		UO251 = self.massPeaks[self.uranium_peak_name]
		key = "cpsErrorWeighted"
		self.data["ThThActivityRatio"]= activityRatio(*ThO246.data[key],TH230_DECAY_CONSTANT,TH230_DECAY_CONSTANT_ERROR, *ThO248.data[key],TH232_DECAY_CONSTANT, TH232_DECAY_CONSTANT_ERROR)
		self.data["UThActivityRatio"] = activityRatio(*UO251.data[key],U238_DECAY_CONSTANT,U238_DECAY_CONSTANT_ERROR, *ThO248.data[key],TH232_DECAY_CONSTANT, TH232_DECAY_CONSTANT_ERROR)
		